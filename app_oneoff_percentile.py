import streamlit as st
import random
import time
from collections import Counter
import pandas as pd

st.set_page_config(page_title="FF Combat One-Off (Flat %)", layout="centered")
st.title("FF Single Roll Combat Calculator")

# --- Inputs ---
col1, col2 = st.columns([1, 2])
with col1:
    pSkill = st.slider("Player Skill", 1, 24, 10)
    pStamina = st.slider("Player Stamina", 1, 36, 20)
    pLuck = st.slider("Player Luck", 1, 18, 9)

    mSkill = st.slider("Monster Skill", 1, 24, 7)
    mStamina = st.slider("Monster Stamina", 1, 48, 8)

    UseLucktoDamage = st.checkbox("Always use Luck when damaging", False)
    UseLucktoKill = st.checkbox("Use Luck only to Kill", True)

    UseLucktoAvoidWounds = st.checkbox("Always use Luck when wounded", False)
    UseLucktoSurvive = st.checkbox("Use Luck only to Survive", True)

    nFights = st.number_input("Number of Fights to Simulate", 1, 100000, 10000, step=100)

# --- Functions (moved outside of col1) ---
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
            if (UseLucktoDamage or (UseLucktoKill and mStamina == 3)) and pLuck >= 1:
                luck_bonus = testLuck(pLuck)
                mStamina -= (2 + luck_bonus)
                pLuck -= 1
            else:
                mStamina -= 2
        elif pAttack < mAttack:
            if (UseLucktoAvoidWounds or (UseLucktoSurvive and pStamina == 2)) and pLuck >= 1:
                luck_bonus = testLuck(pLuck)
                pStamina -= (2 - luck_bonus)
                pLuck -= 1
            else:
                pStamina -= 2

def evaluate_one_off(pSkill, pStamina, pLuck, mSkill, mStamina, UseLucktoDamage, UseLucktoKill, UseLucktoAvoidWounds, UseLucktoSurvive, nFights):
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
        else:
            result_pair_counter[(0, 0)] += 1
            player_result_pairs.append((0, 0))

    n_wins = sum(1 for stamina, _ in player_result_pairs if stamina > 0)
    win_rate = (n_wins / nFights) * 100

    st.subheader("Single Roll Fight Simulator")

    # Styled Player and Monster Stat Blocks
    st.markdown(f"""
    <div style="border:1px solid #888;padding:10px;border-radius:10px;background-color:#111111">
        <b>⚔️ Player Stats</b><br>
        <span style="font-size:2rem;">
            Skill: {pSkill} &nbsp;&nbsp;&nbsp; Stamina: {pStamina} &nbsp;&nbsp;&nbsp; Luck: {pLuck}
        </span>
    </div><br>
    <div style="border:1px solid #888;padding:10px;border-radius:10px;background-color:#1a1a1a">
        <b>💀 Monster Stats</b><br>
         <span style="font-size:2rem;">
            Skill: {mSkill} &nbsp;&nbsp;&nbsp; Stamina: {mStamina}
         </span>
    </div><br>
    """, unsafe_allow_html=True)

    #st.markdown(f"""
    #**Options:**  
    #• UseLucktoKill: `{UseLucktoKill}`  
    #• UseLucktoSurvive: `{UseLucktoSurvive}`  
    #**Fights Simulated:** {nFights}  
    #**Time Taken:** {total_duration:.2f} seconds
    #""")

    st.markdown(f"""
    **Options:**  
    • UseLucktoKill: `{UseLucktoKill}`  
    • UseLucktoSurvive: `{UseLucktoSurvive}`  
    • UseLucktoDamage: `{UseLucktoDamage}`  
    • UseLucktoAvoidWounds: `{UseLucktoAvoidWounds}`  
    **Fights Simulated:** {nFights}  
    **Player Win Rate:** {win_rate:.1f}%  
    **Time Taken:** {total_duration:.2f} seconds
    """)

    total = sum(result_pair_counter.values())
    expanded = []
    for pair, count in sorted(result_pair_counter.items()):
        expanded.extend([pair] * count)
    expanded.sort()

    actual_percent = random.random()
    percentile_index = int(actual_percent * len(expanded)) if expanded else -1

    if expanded and percentile_index < len(expanded):
        mapped_outcome = expanded[percentile_index]
    else:
        mapped_outcome = ("0", "0")

    st.markdown(f"""
    <div style="border:1px dashed #666;padding:10px;margin-top:15px;border-radius:10px;background-color:#222;">
        🎲 <b>Random Roll:</b> {actual_percent:.2%}<br>
        🧾 <b>Player Stats after fight:</b><br>
        <span style="font-size:2rem;">
            Skill: <b>{pSkill}</b> &nbsp;&nbsp;&nbsp; 
            Stamina: <b>{mapped_outcome[0]}</b> &nbsp;&nbsp;&nbsp; 
            Luck: <b>{mapped_outcome[1]}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    if mapped_outcome == (0, 0):
        st.markdown("<br><span style='color:red; font-weight:bold;'>Your Adventure Ends Here, slain in combat.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<br><span style='color:limegreen; font-weight:bold;'>You have defeated your opponent!</span>", unsafe_allow_html=True)

# --- Run button ---
if st.button("Run Simulation"):
    with col2:
        evaluate_one_off(
            pSkill=pSkill,
            pStamina=pStamina,
            pLuck=pLuck,
            mSkill=mSkill,
            mStamina=mStamina,
            UseLucktoDamage=UseLucktoDamage,
            UseLucktoKill=UseLucktoKill,
            UseLucktoAvoidWounds=UseLucktoAvoidWounds,
            UseLucktoSurvive=UseLucktoSurvive,
            nFights=nFights
        )
