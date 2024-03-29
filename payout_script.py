from orderbook_api import get_solver_competition_data
from gnosis_scan_apy import fetch_hashes
import threading
from time import sleep
from constants import UPPER_PERFORMANCE_REWARD_CAP, LOWER_PERFORMANCE_REWARD_CAP, BUDGET

result = []

def settlement_performance_reward(tx_hash: str):
    """
    This function computes the performance reward associated
    with a successful settlement
    """
    global result
    #print(tx_hash)
    data, environment = get_solver_competition_data(tx_hash)
    if data == None:
        return {
            "status": False,
            "performance_reward": 0,
            "solver": None,
            "participation": None,
        }
    winning_solution = data["solutions"][-1]
    winning_score = int(winning_solution["score"])
    winning_solver = winning_solution["solver"]
    reference_score = 0
    participating_non_winning_solvers = []
    for s in data["solutions"]:
        name = s["solver"]
        if name not in participating_non_winning_solvers and name != winning_solver:
            participating_non_winning_solvers.append(name)
    if len(data["solutions"]) > 1:
        reference_score = int(data["solutions"][-2]["score"])
    performance_reward = winning_score - reference_score
    if performance_reward > UPPER_PERFORMANCE_REWARD_CAP:
        performance_reward = UPPER_PERFORMANCE_REWARD_CAP
    elif performance_reward < LOWER_PERFORMANCE_REWARD_CAP:
        performance_reward = LOWER_PERFORMANCE_REWARD_CAP
    result.append({
        "status": True,
        "performance_reward": performance_reward,
        "solver": winning_solver,
        "participation": participating_non_winning_solvers,
    })


def compute_payouts() -> any:
    """
    For now, this form of the payout ignores reverts/failures.
    """
    tx_hashes = fetch_hashes(32765842,32783122)
    perfomance_rewards = {}
    consistency_rewards = {}
    num_hashes = len(tx_hashes)
    i = 0
    global result
    result = []
    while i < num_hashes:
        j = 0
        while i < num_hashes and j < 5:
            i = i + 1
            j = j + 1
        threads = []
        for t in range(j):
            try:
                threads.append(threading.Thread(target=settlement_performance_reward(tx_hashes[i - j + t])))
            except Exception as e:
                print(j,e)
                exit()
        for t in range(j):
            try:
                threads[t].start()
            except Exception as e:
                print(t,e)
                exit()
        for t in range(j):
            try:
                threads[t].join()
            except Exception as e:
                print(t,e)
                exit()      
        sleep(1)
        
        for res in result:
            if i > 50 and i < 55:
                print(res)
            try:
                if not res["status"]:
                    print("Issue with data fetching. Skipping hash " + res)
                    continue
                solver = res["solver"]
                reward = res["performance_reward"]
                participation = res["participation"]
                if solver not in perfomance_rewards:
                    perfomance_rewards[solver] = reward
                else:
                    perfomance_rewards[solver] += reward
                for l in participation:
                    if l not in consistency_rewards:
                        consistency_rewards[l] = 1
                    else:
                        consistency_rewards[l] += 1
            except Exception as e:
                print(e)
                exit()

    total_performance_rewards = 0
    for s in perfomance_rewards:
        total_performance_rewards += perfomance_rewards[s]
    consistency_budget = 0
    if total_performance_rewards < BUDGET:
        consistency_budget = BUDGET - total_performance_rewards
        total_participation = 0
        for s in consistency_rewards:
            total_participation += consistency_rewards[s]
        for s in consistency_rewards:
            consistency_rewards[s] = (
                consistency_rewards[s] * consistency_budget / total_participation
            )

    total_rewards = {}
    for s in perfomance_rewards:
        total_rewards[s] = perfomance_rewards[s]
    if consistency_budget > 0:
        for s in consistency_rewards:
            if s in total_rewards:
                total_rewards[s] += consistency_rewards[s]
            else:
                total_rewards[s] = consistency_rewards[s]
    return total_rewards


def main() -> None:
    print(compute_payouts())

if __name__ == "__main__":
    # sleep time can be set here in seconds
    main()