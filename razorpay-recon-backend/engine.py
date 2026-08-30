import pandas as pd
from thefuzz import fuzz
import asyncio
from typing import Callable, Awaitable
from groq import Groq
import os

from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ReconciliationEngine:
    def __init__(self, internal_df: pd.DataFrame, bank_df: pd.DataFrame):
        self.internal_df = internal_df.copy()
        self.bank_df = bank_df.copy()
        self.internal_df['matched'] = False
        self.bank_df['matched'] = False
        self.results = []

    def calculate_confidence(self, int_row, bank_row) -> tuple[float, list[str]]:
        """Calculates match confidence and provides explainable reasons."""
        score = 0.0
        reasons = []

        # 1. Exact Amount Match (50 points)
        if abs(int_row['amount'] - bank_row['amount']) < 0.01:
            score += 50
            reasons.append("Exact Amount Match")
        
        # 2. Date Proximity (20 points)
        date_diff = abs((int_row['date'] - bank_row['date']).days)
        if date_diff == 0:
            score += 20
            reasons.append("Exact Date Match")
        elif date_diff <= 2:
            score += 10
            reasons.append(f"Date within {date_diff} days")

        # 3. Fuzzy Text Matching on Description/Reference (30 points)
        # Combining description and reference for better context
        int_text = f"{int_row.get('description', '')} {int_row.get('reference', '')}"
        bank_text = f"{bank_row.get('description', '')} {bank_row.get('reference', '')}"
        
        text_score = fuzz.token_set_ratio(int_text.lower(), bank_text.lower())
        text_points = (text_score / 100) * 30
        score += text_points
        
        if text_score > 80:
            reasons.append(f"High Text Similarity ({text_score}%)")
        elif text_score > 50:
            reasons.append(f"Partial Text Match ({text_score}%)")

        return round(score, 2), reasons

    async def generate_ai_reasoning(self, int_row, bank_row, confidence_score, reasons):
        """Uses GenAI to generate human-readable explanation for exceptions"""
        if confidence_score >= 75:
            return None  # No need for AI reasoning if already matched
        
        prompt = f"""
        You are a financial reconciliation expert AI. Analyze these two transaction records:
        
        Internal Record:
        - Amount: {int_row.get('amount', 'N/A')}
        - Date: {int_row.get('date', 'N/A')}
        - Description: {int_row.get('description', 'N/A')}
        - Reference: {int_row.get('reference', 'N/A')}
        
        Bank Record:
        - Amount: {bank_row.get('amount', 'N/A')}
        - Date: {bank_row.get('date', 'N/A')}
        - Description: {bank_row.get('description', 'N/A')}
        - Reference: {bank_row.get('reference', 'N/A')}
        
        Current Match Confidence: {confidence_score}%
        Existing Reasons: {', '.join(reasons)}
        
        Provide a concise 2-sentence explanation:
        1. Why might these records match or not match?
        2. What action should a human reviewer take?
        
        Keep it professional and specific to fintech reconciliation.
        """
        
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",  # <--- YEH 100% STABLE HAI
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI Analysis failed: {str(e)}"

    async def process(self, progress_callback: Callable[[str], Awaitable[None]]):
        """Runs the reconciliation logic and streams progress."""
        total_internal = len(self.internal_df)
        processed = 0

        # Phase 1: Exact Matching (Fast path)
        await progress_callback("Starting Exact Match Phase...")
        for idx, int_row in self.internal_df.iterrows():
            if int_row['matched']: continue
            
            # Find exact matches in bank statement
            exact_matches = self.bank_df[
                (self.bank_df['amount'] == int_row['amount']) & 
                (self.bank_df['date'] == int_row['date']) &
                (~self.bank_df['matched'])
            ]
            
            if not exact_matches.empty:
                bank_idx = exact_matches.index[0]
                bank_row = self.bank_df.loc[bank_idx]
                
                self.internal_df.at[idx, 'matched'] = True
                self.bank_df.at[bank_idx, 'matched'] = True
                
                self.results.append({
                    "internal_id": int_row.get('id', idx),
                    "bank_id": bank_row.get('id', bank_idx),
                    "confidence_score": 100.0,
                    "status": "MATCHED",
                    "reasons": ["Exact Match (Amount + Date)"]
                })

            processed += 1
            if processed % 100 == 0:
                await progress_callback(f"Exact Match: {processed}/{total_internal} records processed.")
                await asyncio.sleep(0.1) # Simulate processing time / yield to event loop

        # Phase 2: Fuzzy Matching for Exceptions (AI path)
        await progress_callback("Starting AI Fuzzy Match Phase for unresolved records...")
        unmatched_internal = self.internal_df[~self.internal_df['matched']]
        unmatched_bank = self.bank_df[~self.bank_df['matched']]
        
        fuzzy_processed = 0
        for idx, int_row in unmatched_internal.iterrows():
            best_score = 0
            best_match = None
            best_reasons = []

            for b_idx, bank_row in unmatched_bank.iterrows():
                score, reasons = self.calculate_confidence(int_row, bank_row)
                if score > best_score:
                    best_score = score
                    best_match = (b_idx, bank_row)
                    best_reasons = reasons

            # Thresholding: 75.0 is the cutoff for auto-match
            if best_score >= 75.0 and best_match:
                b_idx, bank_row = best_match
                self.internal_df.at[idx, 'matched'] = True
                self.bank_df.at[b_idx, 'matched'] = True
                
                self.results.append({
                    "internal_id": int_row.get('id', idx),
                    "bank_id": bank_row.get('id', b_idx),
                    "confidence_score": best_score,
                    "status": "MATCHED",
                    "reasons": best_reasons
                })
            else:
                # Route to Exception List with AI Analysis
                ai_reasoning = None
                if best_match:
                    b_idx, bank_row = best_match
                    ai_reasoning = await self.generate_ai_reasoning(int_row, bank_row, best_score, best_reasons)
                
                self.results.append({
                    "internal_id": int_row.get('id', idx),
                    "bank_id": None,
                    "confidence_score": best_score if best_match else 0.0,
                    "status": "EXCEPTION",
                    "reasons": best_reasons if best_match else ["No viable match found"],
                    "ai_analysis": ai_reasoning  # New field for GenAI reasoning
                })

            fuzzy_processed += 1
            if fuzzy_processed % 50 == 0:
                await progress_callback(f"AI Fuzzy Match: {fuzzy_processed}/{len(unmatched_internal)} records processed.")
                await asyncio.sleep(0.05)

        await progress_callback("Reconciliation Complete!")
        return self.results