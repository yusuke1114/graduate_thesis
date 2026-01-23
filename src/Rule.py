import random
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import scipy.stats as stats 
import pickle
import csv


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
    
class RuleTrader:
    """ ルールベース・プレイヤー """
    def __init__(self, agent_id, initial_asset):
        self.id = agent_id
        self.asset = initial_asset
        self.has_traded = False
        self.type = "Rule" 

    def reset_period(self):
        self.has_traded = False

    def choose_action(self, board):
        chosen_price = random.randint(PRICE_RANGE[0] + 1, PRICE_MAX - 1)
        board_type = board['type']
        
        if board_type == 'empty':
            return random.choice(['buyer', 'seller']), chosen_price
        
        board_price = board['price']
        
        if board_type == 'ask': # 板は「売り」
            if chosen_price >= board_price:
                return 'buyer', chosen_price # 成立
            else:
                return 'seller', chosen_price # 上書き
                
        elif board_type == 'bid': # 板は「買い」
            if chosen_price <= board_price:
                return 'seller', chosen_price # 成立
            else:
                return 'buyer', chosen_price # 上書き



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
            
            if isinstance(agent, RuleTrader):
                role, price = agent.choose_action(board)
            else:
                role, price = agent.choose_action()
            
            # ログ用変数
            log_price = price
            result_type = "fail"
            passive_log_entry = None # 相手側のログ用

            if role == 'buyer':
                if board['type'] == 'ask' and price >= board['price']:
                    if board['agent_id'] != -1 and not traders_list[board['agent_id']].has_traded:
                        # --- 取引成立 ---
                        seller = traders_list[board['agent_id']] 
                        
                        agent.has_traded = True
                        seller.has_traded = True
                        
                        trade_price = board['price'] # 約定価格
                        
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
                        # --- 取引成立 ---
                        buyer = traders_list[board['agent_id']]
                        
                        agent.has_traded = True
                        buyer.has_traded = True
                        
                        trade_price = board['price'] # 約定価格
                        
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

            # 1. 能動的エージェントのログ追加
            full_logs.append([period+1, step+1, agent.id, agent.type, role, log_price, result_type])
            
            # 2. 受動的エージェント（相手）がいる場合、そのログも追加
            if passive_log_entry is not None:
                full_logs.append(passive_log_entry)
        
        if (period + 1) % 10 == 0:
            print(f" ... 期間 {period + 1}/{num_periods} 完了")

    return traders_list, full_logs


def save_cdf_data_file(data, filename):

    if len(data) == 0: return
    
    data_mean = np.mean(data)
    data_std = np.std(data)
    if data_std == 0: return

    # 標準化 & 絶対値
    standardized_data = np.abs([(x - data_mean) / data_std for x in data])
    sorted_data = np.sort(standardized_data)
    
    n = len(data)
    y_values = 1.0 - (np.arange(n) / n)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        f.write("# Normalized_Asset_Abs CCDF_Value\n")
        for x, y in zip(sorted_data, y_values):
            if x > 0: 
                f.write(f"{x} {y}\n")
    print(f"資産CCDF DAT保存: {filename}")

def save_raw_asset_data(data, filename):

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write("# Raw Asset Values\n")
        for val in data:
            f.write(f"{val}\n")
    print(f"資産生データ(Raw)保存: {filename}")

def save_gaussian_reference(filename):

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    x_th = np.logspace(-2, 1, 100)
    y_th = 2 * stats.norm.sf(x_th)
    
    with open(filename, 'w') as f:
        f.write("# Gaussian_X Gaussian_Y(CCDF)\n")
        for x, y in zip(x_th, y_th):
            f.write(f"{x} {y}\n")
    print(f"正規分布理論値保存: {filename}")


def plot_and_save_graph(traders_list, title, output_filename):

    final_assets = [t.asset for t in traders_list]
    
    data_mean = np.mean(final_assets)
    data_std = np.std(final_assets)
    
    if data_std == 0: return

    # 全体での正規化
    std_data = np.abs([(x - data_mean) / data_std for x in final_assets])
    sorted_data = np.sort(std_data)
    y_values = 1.0 - (np.arange(len(sorted_data)) / len(sorted_data))
    
    # 理論値
    x_th = np.logspace(-2, 1, 100)
    y_th = 2 * stats.norm.sf(x_th)

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_data, y_values, 'b.', label='Simulation (All)', markersize=3)
    plt.plot(x_th, y_th, 'r--', label='Normal Dist')
    plt.xscale('log'); plt.yscale('log')
    plt.title(title)
    plt.xlabel('|Normalized Asset| (All Traders)')
    plt.ylabel('CCDF')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.xlim(0.01, 10); plt.ylim(0.001, 2)
    
    plt.savefig(output_filename)
    plt.close()
    print(f"グラフPNG保存(全体版): {output_filename}")


def analyze_and_save_graph(logs, label, output_dir="fig"):
    os.makedirs(output_dir, exist_ok=True)
    
    stats = {
        'ZIT':  {'Sell Exec': 0, 'Sell Over': 0, 'Buy Exec': 0, 'Buy Over': 0, 'Fail': 0},
        'Rule': {'Sell Exec': 0, 'Sell Over': 0, 'Buy Exec': 0, 'Buy Over': 0, 'Fail': 0}
    }
    
    for row in logs:
        agent_type = row[3]
        role = row[4]
        result = row[6]
        
        if result == 'fail':
            stats[agent_type]['Fail'] += 1
        elif role == 'buyer':
            if result == 'executed':
                stats[agent_type]['Buy Exec'] += 1
            elif result == 'overwrite':
                stats[agent_type]['Buy Over'] += 1
        elif role == 'seller':
            if result == 'executed':
                stats[agent_type]['Sell Exec'] += 1
            elif result == 'overwrite':
                stats[agent_type]['Sell Over'] += 1

    dat_filename = os.path.join(output_dir, f"action_stats_{label}.dat")
    with open(dat_filename, "w") as f:
        f.write("# Type Fail Buy_Over Buy_Exec Sell_Over Sell_Exec\n")
        for t_type in ['ZIT', 'Rule']:
            d = stats[t_type]
            line = f"{t_type} {d['Fail']} {d['Buy Over']} {d['Buy Exec']} {d['Sell Over']} {d['Sell Exec']}\n"
            f.write(line)
    print(f"行動統計DAT保存: {dat_filename}")

    pdf_filename = os.path.join(output_dir, f"action_graph_{label}.pdf")
    
    types = ['ZIT', 'Rule']
    sell_exec = [stats[t]['Sell Exec'] for t in types]
    sell_over = [stats[t]['Sell Over'] for t in types]
    buy_exec  = [stats[t]['Buy Exec'] for t in types]
    buy_over  = [stats[t]['Buy Over'] for t in types]
    fail      = [stats[t]['Fail'] for t in types]

    bottom_1 = np.array(fail)
    bottom_2 = bottom_1 + np.array(buy_over)
    bottom_3 = bottom_2 + np.array(buy_exec)
    bottom_4 = bottom_3 + np.array(sell_over)

    plt.figure(figsize=(8, 6))
    bar_width = 0.5
    
    plt.bar(types, fail, width=bar_width, color='gray', label='Fail')
    plt.bar(types, buy_over, bottom=bottom_1, width=bar_width, color='lightblue', label='Buy Overwrite')
    plt.bar(types, buy_exec, bottom=bottom_2, width=bar_width, color='tab:blue', label='Buy Executed')
    plt.bar(types, sell_over, bottom=bottom_3, width=bar_width, color='orange', label='Sell Overwrite')
    plt.bar(types, sell_exec, bottom=bottom_4, width=bar_width, color='tab:red', label='Sell Executed')

    plt.title(f"Action Pattern Breakdown (Rule: {label})")
    plt.ylabel("Count")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.tight_layout()
    
    plt.savefig(pdf_filename)
    plt.close()
    print(f"行動グラフPDF保存: {pdf_filename}")


if __name__ == '__main__':
    
    TOTAL_TRADERS = 2000    
    NUM_PERIODS = 100       
    STEPS_PER_PERIOD = TOTAL_TRADERS * 2 
    
    output_dir = "fig"
    os.makedirs(output_dir, exist_ok=True)

    save_gaussian_reference(f"{output_dir}/gaussian_theory.dat")

    print(f"\n--- Rule Trader シミュレーション開始 (出力先: {output_dir}) ---")
    
    rule_percentages = [0.1, 0.2, 0.3, 0.4, 0.5] 

    for pct in rule_percentages:
        label = f"{int(pct*100)}pct"
        print(f"\n=== Rule割合: {int(pct*100)}% ===")
        
        num_rule = int(TOTAL_TRADERS * pct)
        num_zit = TOTAL_TRADERS - num_rule
        
        mixed_traders = []
        for i in range(num_rule):
            mixed_traders.append(RuleTrader(i, INITIAL_ASSET))
        for i in range(num_zit):
            mixed_traders.append(ZITrader(i + num_rule, INITIAL_ASSET))
            
        final_traders, logs = run_mixed_simulation(mixed_traders, NUM_PERIODS, STEPS_PER_PERIOD)
        

        pkl_name = f'results_Rule_{label}.pkl'
        with open(pkl_name, 'wb') as f:
            pickle.dump(final_traders, f)
        print(f"PKL保存: {pkl_name}")


        csv_name = f'trade_history_Rule_{label}.csv'
        with open(csv_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Period", "Step", "AgentID", "Type", "Role", "Price", "Result"])
            writer.writerows(logs)
        print(f"CSV保存: {csv_name}")


        all_assets = [t.asset for t in final_traders]
        
        save_cdf_data_file(all_assets, f"{output_dir}/asset_ccdf_{label}_all.dat")

        save_raw_asset_data(all_assets, f"{output_dir}/asset_raw_{label}_all.dat")

        plot_and_save_graph(final_traders, f"Rule {label} Asset Distribution (All)", f"{output_dir}/asset_dist_{label}.png")

        analyze_and_save_graph(logs, label, output_dir=output_dir)

    print("全シミュレーション完了")