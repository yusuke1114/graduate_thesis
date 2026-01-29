import random
import numpy as np
import sys
from collections import Counter

# --- 定数 ---
MAX_PRICE = 200 

# --- エージェントクラス ---
class ZeroIntelligenceTrader:
    def __init__(self, agent_id):
        self.id = agent_id
        self.cost = random.randint(0, MAX_PRICE)
        self.value = random.randint(self.cost, MAX_PRICE)

    def get_buy_price(self):
        return random.randint(0, self.value)

    def get_sell_price(self):
        return random.randint(self.cost, MAX_PRICE)

def encode_input_vector(board, agent_action):

    # 1. 板の状態 (3 + 201 = 204次元)
    # [空, 売り, 買い] + [価格0, ..., 価格200]
    board_vec = np.zeros(3 + (MAX_PRICE + 1)) 
    if board['type'] == 'empty':
        board_vec[0] = 1
    elif board['type'] == 'ask': # 売り板
        board_vec[1] = 1
        board_vec[3 + board['price']] = 1
    elif board['type'] == 'bid': # 買い板
        board_vec[2] = 1
        board_vec[3 + board['price']] = 1

    # 2. エージェントの行動 (2 + 201 = 203次元)
    # [買い, 売り] + [価格0, ..., 価格200]
    action_vec = np.zeros(2 + (MAX_PRICE + 1)) 
    if agent_action['role'] == 'buyer':
        action_vec[0] = 1
        action_vec[2 + agent_action['price']] = 1
    elif agent_action['role'] == 'seller':
        action_vec[1] = 1
        action_vec[2 + agent_action['price']] = 1
    
    # 結合して407次元ベクトルを返す
    return np.concatenate([board_vec, action_vec])

def run_market_simulation(num_traders, num_steps):
    traders = [ZeroIntelligenceTrader(i) for i in range(num_traders)]
    board = {'type': 'empty', 'price': -1}
    x_data, y_data = [], []

    print(f"シミュレーション開始 (Steps: {num_steps}, Traders: {num_traders})")
    for _ in range(num_steps):
        agent = random.choice(traders)
        role = random.choice(['buyer', 'seller'])
        
        if role == 'buyer':
            price = agent.get_buy_price()
        else: # seller
            price = agent.get_sell_price()
        
        agent_action = {'role': role, 'price': price}

        x_data.append(encode_input_vector(board, agent_action))

        # 0:売り上書き, 1:買い上書き, 2:売り成立, 3:買い成立, 4:不成立
        
        if role == 'buyer':
            if board['type'] == 'ask' and price >= board['price']:
                y_data.append(3) 
                board = {'type': 'empty', 'price': -1}
            
            elif (board['type'] == 'bid' and price > board['price']) or board['type'] == 'empty':
                y_data.append(1) 
                board = {'type': 'bid', 'price': price}
            else:
                y_data.append(4) 
                pass 

        else: # seller

            if board['type'] == 'bid' and price <= board['price']:
                y_data.append(2)
                board = {'type': 'empty', 'price': -1} 

            elif (board['type'] == 'ask' and price < board['price']) or board['type'] == 'empty':
                y_data.append(0)
                board = {'type': 'ask', 'price': price} 

            else:
                y_data.append(4) 
                pass 

    print(f"データ生成完了")
    return np.array(x_data), np.array(y_data)

if __name__ == "__main__":

    NUM_DATASETS = 20    
    NUM_TRADERS = 2000    
    SIMULATION_STEPS = 50000

    print(f"合計 {NUM_DATASETS} セットのデータを連続生成します")

    for i in range(NUM_DATASETS):
        SEED_VALUE = i  
        
        # シードの設定
        random.seed(SEED_VALUE)
        np.random.seed(SEED_VALUE)

        print(f"--- [Set {i+1}/{NUM_DATASETS}] Seed={SEED_VALUE} ---")
        
        # シミュレーション実行
        x_data, y_data = run_market_simulation(NUM_TRADERS, SIMULATION_STEPS)
        
        # ファイル名決定 
        x_data_filename = f"x_data_{SEED_VALUE:02d}.npy"
        y_data_filename = f"y_data_{SEED_VALUE:02d}.npy"
        
        # 保存
        np.save(x_data_filename, x_data)
        np.save(y_data_filename, y_data)
        print(f"保存完了: {x_data_filename}, {y_data_filename}\n")

    print("全データの生成が完了しました")