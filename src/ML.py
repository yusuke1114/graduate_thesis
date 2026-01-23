import random
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import sys
import os
import scipy.stats as stats 
import pickle
import csv

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'


PRICE_RANGE = (0, 200)
PRICE_MAX = 200
INITIAL_ASSET = 500.0


class ZITrader:
    """ ZITエージェント """
    def __init__(self, agent_id, initial_asset):
        self.id = agent_id
        self.asset = initial_asset
        self.has_traded = False
        self.type = "ZIT"
        self.cost = 0
        self.value = 0
        self.buy_price = 0
        self.sell_price = 0
        self.reset_period()

    def reset_period(self):
        self.has_traded = False
        self.cost = random.randint(PRICE_RANGE[0], PRICE_MAX)
        self.value = random.randint(PRICE_RANGE[0], PRICE_MAX)
        if self.value < self.cost:
            self.value = random.randint(self.cost, PRICE_MAX)
        self.buy_price = random.randint(0, self.value)
        self.sell_price = random.randint(self.cost, PRICE_MAX)

    def choose_action(self):
        role = random.choice(['buyer', 'seller'])
        price = self.buy_price if role == 'buyer' else self.sell_price
        return role, price
    
class MLTrader:
    """ MLプレイヤー """
    def __init__(self, agent_id, initial_asset, model):
        self.id = agent_id
        self.asset = initial_asset
        self.has_traded = False
        self.model = model
        self.type = "ML"

    def reset_period(self):
        self.has_traded = False

    def choose_action(self, board):
        chosen_price = random.randint(PRICE_RANGE[0] + 1, PRICE_MAX - 1)
        action_buy = {'role': 'buyer', 'price': chosen_price}
        action_sell = {'role': 'seller', 'price': chosen_price}
        
        x_buy = encode_input_vector(board, action_buy).reshape(1, -1)
        x_sell = encode_input_vector(board, action_sell).reshape(1, -1)
        
        inputs = np.vstack([x_buy, x_sell])
        probs = self.model.predict(inputs, verbose=0)
        
        prob_success_buy = 1.0 - probs[0][4]
        prob_success_sell = 1.0 - probs[1][4]

        if prob_success_buy > prob_success_sell:
            return 'buyer', chosen_price
        else:
            return 'seller', chosen_price


def encode_input_vector(board, agent_action):
    board_vec = np.zeros(3 + (PRICE_MAX + 1)) 
    if board['type'] == 'empty':
        board_vec[0] = 1
    elif board['type'] == 'ask':
        board_vec[1] = 1; board_vec[3 + board['price']] = 1
    elif board['type'] == 'bid':
        board_vec[2] = 1; board_vec[3 + board['price']] = 1
    action_vec = np.zeros(2 + (PRICE_MAX + 1)) 
    if agent_action['role'] == 'buyer':
        action_vec[0] = 1; action_vec[2 + agent_action['price']] = 1
    elif agent_action['role'] == 'seller':
        action_vec[1] = 1; action_vec[2 + agent_action['price']] = 1
    return np.concatenate([board_vec, action_vec])

def run_mixed_simulation(traders_list, num_periods, steps_per_period):
    full_logs = [] 
    for period in range(num_periods):
        for agent in traders_list:
            agent.reset_period()
        board = {'type': 'empty', 'price': -1, 'agent_id': -1}
        
        for step in range(steps_per_period):
            available_traders = [t for t in traders_list if not t.has_traded]
            if not available_traders: break 
            agent = random.choice(available_traders)
            
            if isinstance(agent, MLTrader):
                role, price = agent.choose_action(board)
            else:
                role, price = agent.choose_action()
            
            log_price = price 
            result_type = "fail"
            passive_log_entry = None 

            if role == 'buyer':
                if board['type'] == 'ask' and price >= board['price']:
                    if board['agent_id'] != -1 and not traders_list[board['agent_id']].has_traded:

                        seller = traders_list[board['agent_id']] 
                        agent.has_traded = True
                        seller.has_traded = True
                        trade_price = board['price']
                        
                        agent.asset -= trade_price
                        seller.asset += trade_price
                        
                        result_type = "executed"
                        log_price = trade_price 

                        passive_log_entry = [
                            period+1, step+1, seller.id, seller.type, 'seller', trade_price, "executed"
                        ]
                        
                        board = {'type': 'empty', 'price': -1, 'agent_id': -1}
                    else:
                        result_type = "fail"
                elif (board['type'] == 'bid' and price > board['price']) or board['type'] == 'empty':
                    board = {'type': 'bid', 'price': price, 'agent_id': agent.id}
                    result_type = "overwrite"
                else:
                    result_type = "fail"

            elif role == 'seller':
                if board['type'] == 'bid' and price <= board['price']:
                    if board['agent_id'] != -1 and not traders_list[board['agent_id']].has_traded:

                        buyer = traders_list[board['agent_id']]
                        agent.has_traded = True
                        buyer.has_traded = True
                        trade_price = board['price']
                        
                        agent.asset += trade_price
                        buyer.asset -= trade_price
                        
                        result_type = "executed"
                        log_price = trade_price

                        passive_log_entry = [
                            period+1, step+1, buyer.id, buyer.type, 'buyer', trade_price, "executed"
                        ]

                        board = {'type': 'empty', 'price': -1, 'agent_id': -1}
                    else:
                        result_type = "fail"
                elif (board['type'] == 'ask' and price < board['price']) or board['type'] == 'empty':
                    board = {'type': 'ask', 'price': price, 'agent_id': agent.id}
                    result_type = "overwrite"
                else:
                    result_type = "fail"

            full_logs.append([period+1, step+1, agent.id, agent.type, role, log_price, result_type])
            if passive_log_entry is not None:
                full_logs.append(passive_log_entry)
        
        if (period + 1) % 10 == 0:
            print(f" ... 期間 {period + 1}/{num_periods} 完了")
            
    return traders_list, full_logs


def save_dat_simple(data_list, filename, header=None):

    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            if header: f.write(header + "\n")
            for val in data_list:
                f.write(f"{val}\n")
        print(f"   -> Saved: {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def save_assets(traders, label, out_dir):

    zit_assets = [t.asset for t in traders if t.type == "ZIT"]
    ml_assets  = [t.asset for t in traders if t.type == "ML"]
    all_assets = [t.asset for t in traders]
    
    # 1. 生データ (個別ファイル)
    save_dat_simple([str(x) for x in zit_assets], f"{out_dir}/asset_raw_{label}_zit.dat", "# ZIT Assets")
    save_dat_simple([str(x) for x in ml_assets],  f"{out_dir}/asset_raw_{label}_ml.dat",  "# ML Assets")
    
    # 2. CCDFデータ (全体)
    if len(all_assets) > 0:
        mu = np.mean(all_assets)
        sd = np.std(all_assets)
        if sd > 0:
            norm_assets = np.sort(np.abs([(x - mu) / sd for x in all_assets]))
            y_vals = 1.0 - np.arange(len(all_assets)) / len(all_assets)
            
            ccdf_lines = [f"{x} {y}" for x, y in zip(norm_assets, y_vals) if x > 0]
            save_dat_simple(ccdf_lines, f"{out_dir}/asset_ccdf_{label}_all.dat", "# NormalizedAsset CCDF")

def analyze_and_save_action_stats(logs, label, out_dir):

    stats = {
        'ZIT': {'Fail': 0, 'Buy_Over': 0, 'Buy_Exec': 0, 'Sell_Over': 0, 'Sell_Exec': 0},
        'ML':  {'Fail': 0, 'Buy_Over': 0, 'Buy_Exec': 0, 'Sell_Over': 0, 'Sell_Exec': 0}
    }
    
    for row in logs:
        # row: [Period, Step, AgentID, Type, Role, Price, Result]
        agent_type = row[3]
        role = row[4]
        result = row[6]
        
        if result == 'fail':
            stats[agent_type]['Fail'] += 1
        elif role == 'buyer':
            if result == 'executed':
                stats[agent_type]['Buy_Exec'] += 1
            elif result == 'overwrite':
                stats[agent_type]['Buy_Over'] += 1
        elif role == 'seller':
            if result == 'executed':
                stats[agent_type]['Sell_Exec'] += 1
            elif result == 'overwrite':
                stats[agent_type]['Sell_Over'] += 1
            
    filename = f"{out_dir}/action_stats_{label}.dat"
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:

            f.write("# Type Fail Buy_Over Buy_Exec Sell_Over Sell_Exec\n")
            for t_type in ['ZIT', 'ML']:
                d = stats[t_type]

                f.write(f"{t_type} {d['Fail']} {d['Buy_Over']} {d['Buy_Exec']} {d['Sell_Over']} {d['Sell_Exec']}\n")
        print(f"   -> Action Stats Saved: {filename}")
    except Exception as e:
        print(f"Error saving action stats: {e}")


if __name__ == '__main__':

    out_dir = "fig_ml"
    os.makedirs(out_dir, exist_ok=True)

    x_th = np.logspace(-2, 1, 100)
    y_th = 2 * stats.norm.sf(x_th)
    save_dat_simple([f"{x} {y}" for x, y in zip(x_th, y_th)], f"{out_dir}/gaussian_theory.dat", "# X Y")

    print("--- ML Model Loading ---")
    model_path = 'zit_model_407.keras'
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found.")
        sys.exit(1)
    model = tf.keras.models.load_model(model_path)


    TOTAL_TRADERS = 2000    
    NUM_PERIODS = 100       
    STEPS_PER_PERIOD = TOTAL_TRADERS * 2 
    ML_PERCENTAGE = 0.3
    
    label = f"{int(ML_PERCENTAGE*100)}pct"
    print(f"\n--- Simulation Start: ML Ratio {int(ML_PERCENTAGE*100)}% ---")
 
    num_ml = int(TOTAL_TRADERS * ML_PERCENTAGE)
    num_zit = TOTAL_TRADERS - num_ml
    
    traders = []
    for i in range(num_ml):
        traders.append(MLTrader(i, INITIAL_ASSET, model))
    for i in range(num_zit):
        traders.append(ZITrader(i + num_ml, INITIAL_ASSET))
    
 
    final_traders, full_logs = run_mixed_simulation(traders, NUM_PERIODS, STEPS_PER_PERIOD)
    

    save_assets(final_traders, label, out_dir)
    analyze_and_save_action_stats(full_logs, label, out_dir)
    
    csv_name = f"{out_dir}/trade_history_{label}.csv"
    with open(csv_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Period", "Step", "AgentID", "Type", "Role", "Price", "Result"])
        writer.writerows(full_logs)
    print(f"   -> CSV Saved: {csv_name}")

    print(f" Simulation Completed. All results saved in '{out_dir}/'.")