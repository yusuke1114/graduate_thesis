import random
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import scipy.stats as stats


PRICE_RANGE = (0, 200)
PRICE_MAX = 200
INITIAL_ASSET = 500.0

class ZITrader:
    """ ZITエージェント (修正版: 人為的な範囲制限を撤廃) """
    def __init__(self, agent_id, initial_asset):
        self.id = agent_id
        self.asset = initial_asset
        self.has_traded = False
        self.cost = 0
        self.value = 0
        self.buy_price = 0
        self.sell_price = 0
        self.reset_period()

    def reset_period(self):
        """ 期間ごとに価値とコストをリセット """
        self.has_traded = False
        
        self.cost = random.randint(PRICE_RANGE[0], PRICE_MAX)
        self.value = random.randint(PRICE_RANGE[0], PRICE_MAX)
        
        if self.value < self.cost:
            self.value = random.randint(self.cost, PRICE_MAX)
            
        # 指値の決定
        self.buy_price = random.randint(0, self.value)
        self.sell_price = random.randint(self.cost, PRICE_MAX)

    def choose_action(self):
        role = random.choice(['buyer', 'seller'])
        price = self.buy_price if role == 'buyer' else self.sell_price
        return role, price

    def __repr__(self):
        return f"ZITrader(ID:{self.id}, Asset:{self.asset:.2f}, Traded:{self.has_traded})"


def run_ZIT_simulation(traders_list, num_periods, steps_per_period):
    """
    ZITraderのみの「マルチピリオド」市場を実行する
    """
    
    for period in range(num_periods):
        
        # 各期間の開始時にエージェントの状態（コスト・価値）をリセット
        for agent in traders_list:
            agent.reset_period()
            
        # 板の初期化
        board = {'type': 'empty', 'price': -1, 'agent_id': -1}
        
        for step in range(steps_per_period):
            available_traders = [t for t in traders_list if not t.has_traded]
            if not available_traders:
                break 

            agent = random.choice(available_traders)
            role, price = agent.choose_action()
            
            if role == 'buyer':
                # ケース1: 成立 (Execution) 
                if board['type'] == 'ask' and price >= board['price']: 
                    seller = traders_list[board['agent_id']] 
                    if not seller.has_traded: 
                        agent.has_traded = True
                        seller.has_traded = True
                        trade_price = board['price']
                        agent.asset -= trade_price
                        seller.asset += trade_price
                        board = {'type': 'empty', 'price': -1, 'agent_id': -1} 
                
                # ケース2: 上書き/新規配置 (Overwrite)
                elif board['type'] == 'empty' or (board['type'] == 'bid' and price > board['price']):
                    board = {'type': 'bid', 'price': price, 'agent_id': agent.id} 

                # ケース3: 不成立 (Failure) 
                else:
                    pass

            elif role == 'seller':
                # ケース1: 成立 (Execution) 
                if board['type'] == 'bid' and price <= board['price']: 
                    buyer = traders_list[board['agent_id']]
                    if not buyer.has_traded:
                        agent.has_traded = True
                        buyer.has_traded = True
                        trade_price = board['price']
                        agent.asset += trade_price
                        buyer.asset -= trade_price
                        board = {'type': 'empty', 'price': -1, 'agent_id': -1} 
                
                # ケース2: 上書き/新規配置 (Overwrite)
                elif board['type'] == 'empty' or (board['type'] == 'ask' and price < board['price']): 
                    board = {'type': 'ask', 'price': price, 'agent_id': agent.id} # 板更新

                # ケース3: 不成立 (Failure) 
                else:
                    pass
        
        print(f"  ... 期間 {period + 1}/{num_periods} 完了")

    return traders_list

def create_ccdf_data(standardized_list):
    length = len(standardized_list)
    if length == 0: return np.array([]), np.array([])
    sorted_data = np.sort(standardized_list)
    y_values = 1.0 - (np.arange(length) / length)
    return sorted_data, y_values

def analyze_asset_distribution(final_assets):
    data_mean = np.mean(final_assets)
    data_std = np.std(final_assets)
    if data_std == 0: return np.array([]), np.array([])
    standardized_data = [(x - data_mean) / data_std for x in final_assets]
    abs_data = np.abs(standardized_data)
    return create_ccdf_data(abs_data)

def generate_gaussian_ccdf():
    x_values = np.logspace(-2, 1, 100)
    ccdf_values = 2 * stats.norm.sf(x_values)
    return x_values, ccdf_values

def plot_asset_ccdf(traders_list, title="CCDF"):
    print(f"\n--- グラフ生成中: {title} ---")
    final_assets = [t.asset for t in traders_list]
    
    asset_x, asset_ccdf = analyze_asset_distribution(final_assets)
    gauss_x, gauss_ccdf = generate_gaussian_ccdf() 
    
    plt.figure(figsize=(10, 6))
    if asset_x.size > 0:
        plt.plot(asset_x, asset_ccdf, label='(Asset)', color='blue', marker='.', markersize=2, linestyle='None')
    if gauss_x.size > 0:
        plt.plot(gauss_x, gauss_ccdf, label='N(0, 1) (理論値)', color='red', linestyle='--')
    
    plt.xscale('log'); plt.yscale('log')
    plt.title(title)
    plt.xlabel('標準化された資産 (絶対値)')
    plt.ylabel('相補累積確率 P(X >= x)')
    plt.legend()
    plt.grid(True, which="both", ls="--")
    plt.xlim(0.01, 10); plt.ylim(0.001, 2)
    
    filename = title.replace(" ", "_").replace(":", "").replace("%", "") + ".png"
    try:
        plt.savefig(filename)
        print(f"グラフを '{filename}' として保存しました。")
    except Exception as e:
        print(f"グラフの保存に失敗しました: {e}")
    plt.close()

if __name__ == '__main__':
    
    TOTAL_TRADERS = 2000    
    NUM_PERIODS = 100       
    STEPS_PER_PERIOD = TOTAL_TRADERS * 2 
    
    print("--- ステップ1: ZITのみのベースライン分析 ---")
    
    zit_traders_list = [ZITrader(i, INITIAL_ASSET) for i in range(TOTAL_TRADERS)]
    
    print(f"シミュレーション実行中 (トレーダー: {TOTAL_TRADERS}人, 期間: {NUM_PERIODS})... ")
    final_zit_traders = run_ZIT_simulation(zit_traders_list, NUM_PERIODS, STEPS_PER_PERIOD)
    print("完了。")
    

    final_assets = [t.asset for t in final_zit_traders]
    mu = np.mean(final_assets)
    sigma = np.std(final_assets)
    
    print("\n" + "="*40)
    print(f"【シミュレーション結果統計】")
    print(f"  エージェント数 : {TOTAL_TRADERS}")
    print(f"  平均資産 (μ)   : {mu:.4f}")
    print(f"  標準偏差 (σ)   : {sigma:.4f}")
    print("="*40 + "\n")
    
    plot_asset_ccdf(final_zit_traders, title="ZITのみの資産分布 (ベースライン)")

    print("--- 全ての研究シミュレーションが完了しました。 ---")