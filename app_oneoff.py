
import streamlit as st
import random
import statistics
import time
from collections import Counter
import pandas as pd

st.title("FF Combat Simulator — One-Off 3d6 Outcome")

# --- Sidebar Inputs ---
st.sidebar.title("Player Configuration")
pSkill = st.sidebar.slider("Player Skill", 7, 12, 10)
pStamina = st.sidebar.slider("Player Stamina", 14, 24, 20)
pLuck = st.sidebar.slider("Player Luck", 7, 12, 9)

st.sidebar.title("Monster Configuration")
mSkill = st.sidebar.slider("Monster Skill", 1, 18, 10)
mStamina = st.sidebar.slider("Monster Stamina", 1, 48, 18)

nFights = st.sidebar.number_input("Number of Fights", min_value=1000, max_value=50000, value=10000, step=1000)

UseLucktoKill = st.sidebar.checkbox("Use Luck to Kill (at 3 stamina)", value=True)
UseLucktoSurvive = st.sidebar.checkbox("Use Luck to Survive (take less damage)", value=True)

run_eval = st.sidebar.button("Run Evaluation")

# --- Luck Test ---
def testLuck(pLuck):
    return 1 if (random.randint(1, 6) + random.randint(1, 6)) <= pLuck else 0

# --- Fight Simulation ---
def simulate_fight(pSkill, pStamina, pLuck, mSkill, mStamina, UseLucktoKill, UseLucktoSurvive):
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
            if UseLucktoSurvive and pLuck >= 2:
                luck_bonus = testLuck(pLuck)
                pStamina -= (2 - luck_bonus)
                pLuck -= 1
            else:
                pStamina -= 2

# --- One-off Evaluator ---
def evaluate_one_off(pSkill, pStamina, pLuck, mSkill, mStamina, UseLucktoKill, UseLucktoSurvive, nFights):
    result_pair_counter = Counter()
    total_duration = 0

    for _ in range(nFights):
        current_pStamina = pStamina
        current_pLuck = pLuck
        current_mStamina = mStamina

        start_time = time.time()
        pWin, final_pStamina, final_mStamina, final_pLuck = simulate_fight(
            pSkill, current_pStamina, current_pLuck, mSkill, current_mStamina,
            UseLucktoKill, UseLucktoSurvive)
        end_time = time.time()

        total_duration += (end_time - start_time)

        if pWin:
            pair = (final_pStamina, final_pLuck)
            result_pair_counter[pair] += 1

    # 3d6 probability map
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
        if not expanded:
            mapping[roll] = ("—", "—")
            continue
        while idx < len(cumulative) and cumulative[idx] < cum_threshold:
            idx += 1
        if idx >= len(expanded):
            idx = len(expanded) - 1
        mapping[roll] = expanded[idx]

    # Choose a 3d6 roll
    actual_roll = random.randint(1, 6) + random.randint(1, 6) + random.randint(1, 6)
    mapped_outcome = mapping.get(actual_roll, ("—", "—"))

    st.markdown("### One-Off Evaluation")
    st.write(f"Player: Skill {pSkill}, Stamina {pStamina}, Luck {pLuck}")
    st.write(f"Monster: Skill {mSkill}, Stamina {mStamina}")
    st.write(f"UseLucktoKill: {UseLucktoKill}, UseLucktoSurvive: {UseLucktoSurvive}")
    st.write(f"Fights simulated: {nFights}")
    st.write(f"Time taken: {total_duration:.2f} seconds")
    st.write(f"🎲 Random 3d6 roll: **{actual_roll}**")
    st.write(f"🧾 Mapped outcome: **Stamina {mapped_outcome[0]}, Luck {mapped_outcome[1]}**")
if mapped_outcome == ('—', '—'):
    st.markdown("<br><span style='color:red; font-weight:bold;'>Your Adventure Ends Here, slain in combat.</span>", unsafe_allow_html=True)

if run_eval:
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
