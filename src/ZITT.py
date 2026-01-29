import numpy as np
import tensorflow as tf
from collections import Counter
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input
import glob 
import sys  


SEED_VALUE = 42
np.random.seed(SEED_VALUE)
tf.random.set_seed(SEED_VALUE)

def create_model(input_dim, output_dim):
    model = Sequential([
        Input(shape=(input_dim,)),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(output_dim, activation='softmax')
    ])
    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def manual_under_sampling(X, y):
    counts = Counter(y)
    if len(counts) == 0:
        return X, y
    min_class_count = min(counts.values())
    print(f"各クラスを最小数: {min_class_count} にサンプリングします。")

    sampled_indices = []
    for class_label in counts.keys():
        class_indices = np.where(y == class_label)[0]
        chosen_indices = np.random.choice(class_indices, min_class_count, replace=False)
        sampled_indices.extend(chosen_indices)
    
    np.random.shuffle(sampled_indices)
    return X[sampled_indices], y[sampled_indices]

if __name__ == "__main__":
    
    print(" 学習プロセスを開始します。")
    print("パターンに一致するデータファイルを検索中...")

    x_files = sorted(glob.glob('x_data_*.npy'))
    y_files = sorted(glob.glob('y_data_*.npy'))

    if not x_files:
        print(f"エラー: 'x_data_*.npy' (例: 'x_data_01.npy') という形式のファイルが見つかりません。")
        sys.exit()
    if len(x_files) != len(y_files):
        print(f"エラー: x_data ( {len(x_files)}個) と y_data ( {len(y_files)}個) のファイル数が一致しません。")
        sys.exit()

    print(f"--- 読み込むxデータファイル ({len(x_files)}個) ---")
    print(x_files)
    print(f"--- 読み込むyデータファイル ({len(y_files)}個) ---")
    print(y_files)

    x_data_list = [np.load(f) for f in x_files]
    y_data_list = [np.load(f) for f in y_files]

    x_data = np.concatenate(x_data_list, axis=0)
    y_data = np.concatenate(y_data_list, axis=0)
    
    print(f"合計 {len(x_data)} ステップ分のデータを読み込みました。")


    x_train, x_test, y_train, y_test = train_test_split(
        x_data, y_data, test_size=0.2, random_state=SEED_VALUE, stratify=y_data
    )
    
    print("\n--- 訓練データのクラス内訳（均等化前）---")
    print(sorted(Counter(y_train).items()))
    x_train_resampled, y_train_resampled = manual_under_sampling(x_train, y_train)
    print("--- 訓練データのクラス内訳（均等化後）---")
    print(sorted(Counter(y_train_resampled).items()))

    print("\n--- テストデータのクラス内訳（均等化前）---")
    print(sorted(Counter(y_test).items()))
    x_test_resampled, y_test_resampled = manual_under_sampling(x_test, y_test)
    print("--- テストデータのクラス内訳（均等化後）---")
    print(sorted(Counter(y_test_resampled).items()))


    INPUT_DIM = x_data.shape[1]
    OUTPUT_DIM = len(np.unique(y_data))
    

    if INPUT_DIM != 407:
        print(f" 読み込まれたデータの入力次元が 407 ではありません。(検出値: {INPUT_DIM})")
        
    model = create_model(INPUT_DIM, OUTPUT_DIM)
    
    print("\n--- モデルの学習開始 ---")
    history = model.fit(
        x_train_resampled, y_train_resampled,
        epochs=30,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    model.save('zit_model_407.keras')
    np.save('x_test_resampled.npy', x_test_resampled)
    np.save('y_test_resampled.npy', y_test_resampled)
    print("モデルと均等化済みテストデータを保存しました。")