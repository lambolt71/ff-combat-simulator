
import streamlit as st
import random
import time
from collections import Counter
import pandas as pd

st.set_page_config(page_title="FF Combat One-Off", layout="centered")
st.title("FF Combat Simulator — One-Off 3d6 Outcome")

# --- Inputs ---
col1, col2 = st.columns([1, 2])
with col1:
    pSkill = st.slider("Player Skill", 7, 18, 10)
    pStamina = st.slider("Player Stamina", 14, 24, 20)
    pLuck = st.slider("Player Luck", 7, 12, 9)
    
    mSkill = st.slider("Monster Skill", 1, 18, 10)
    mStamina = st.slider("Monster Stamina", 1, 48, 12)
    
    UseLucktoKill = st.checkbox("Use Luck to Kill", True)
    UseLucktoSurvive = st.checkbox("Use Luck to Survive", True)
    
    nFights = st.number_input("Number of Fights to Simulate", 100, 100000, 10000, step=100)
    
    # --- Simulation Function ---
    def testLuck(pLuck):
        return 1 if (random.randint(1, 6) + random.randint(1, 6)) <= pLuck else 0
    
    def simulate_fight(pSkill, pStamina, pLuck, mSkill, mStamina):
        while True:
            if pStamina <= 0:
                return False, pStamina, mStamina, pLuck
            if mStamina <= 0:
                return True, pStamina, mStamina, pLuck
    
            pAttack = pSkill + random.randint(1, 6) + random.randint(1, 6)
            mAttack = mSkill + random.randint(1, 6) + random.randint(1, 6)
    
            if pAttack > mAttack:
                if UseLucktoKill and mStamina == 3 and pLuck >= 2:
                    luck_bonus = testLuck(pLuck)
                    mStamina -= (2 + luck_bonus)
                    pLuck -= 1
                else:
                    mStamina -= 2
            elif pAttack < mAttack:
                if UseLucktoSurvive and pLuck >= 2 and pStamina == 2:
                    luck_bonus = testLuck(pLuck)
                    pStamina -= (2 - luck_bonus)
                    pLuck -= 1
                else:
                    pStamina -= 2
    
    # --- Evaluation ---
    def evaluate_one_off(pSkill, pStamina, pLuck, mSkill, mStamina, UseLucktoKill, UseLucktoSurvive, nFights):
        player_result_pairs = []
        result_pair_counter = Counter()
        total_duration = 0
    
        for _ in range(nFights):
            current_pStamina = pStamina
            current_pLuck = pLuck
            current_mStamina = mStamina
    
            start = time.time()
            pWin, final_pStamina, final_mStamina, final_pLuck = simulate_fight(
                pSkill, current_pStamina, current_pLuck, mSkill, current_mStamina
            )
            end = time.time()
    
            total_duration += (end - start)
    
            if pWin:
                result_pair_counter[(final_pStamina, final_pLuck)] += 1
                player_result_pairs.append((final_pStamina, final_pLuck))
    
        st.subheader("One-Off Evaluation")
        st.write(f"Player: Skill {pSkill}, Stamina {pStamina}, Luck {pLuck}")
        st.write(f"Monster: Skill {mSkill}, Stamina {mStamina}")
        st.write(f"UseLucktoKill: {UseLucktoKill}, UseLucktoSurvive: {UseLucktoSurvive}")
        st.write(f"Fights simulated: {nFights}")
        st.write(f"Time taken: {total_duration:.2f} seconds")
    
        # 3d6 roll probabilities
        roll_probs = {
            3: 1/216, 4: 3/216, 5: 6/216, 6: 10/216, 7: 15/216, 8: 21/216,
            9: 25/216, 10: 27/216, 11: 27/216, 12: 25/216, 13: 21/216,
            14: 15/216, 15: 10/216, 16: 6/216, 17: 3/216, 18: 1/216
        }
    
        total = sum(result_pair_counter.values())
        expanded = []
        for pair, count in sorted(result_pair_counter.items()):
            expanded.extend([pair] * count)
    
        expanded.sort()
        cumulative = []
        for i, val in enumerate(expanded):
            cumulative.append((i + 1) / total)
    
        mapping = {}
        cum_threshold = 0
        idx = 0
        for roll, prob in roll_probs.items():
            cum_threshold += prob
            while idx < len(cumulative) and cumulative[idx] < cum_threshold:
                idx += 1
            if not expanded:
                mapping[roll] = ("—", "—")
            else:
                mapping[roll] = expanded[min(idx, len(expanded) - 1)]
    
        actual_roll = random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6)
    
        if not expanded:
            mapped_outcome = ("—", "—")
        else:
            mapped_outcome = mapping.get(actual_roll, ("—", "—"))
    
        st.write(f"🎲 Random 3d6 roll: **{actual_roll}**")
        st.write(f"🧾 Mapped outcome: **Stamina {mapped_outcome[0]}, Luck {mapped_outcome[1]}**")
    
        if mapped_outcome == ("—", "—"):
            st.markdown("<br><span style='color:red; font-weight:bold;'>Your Adventure Ends Here, slain in combat.</span>", unsafe_allow_html=True)
    
    if st.button("Run Simulation"):
        with col2:
            evaluate_one_off(
                pSkill=pSkill,
                pStamina=pStamina,
                pLuck=pLuck,
                mSkill=mSkill,
                mStamina=mStamina,
                UseLucktoKill=UseLucktoKill,
                UseLucktoSurvive=UseLucktoSurvive,
                nFights=nFights
            )
