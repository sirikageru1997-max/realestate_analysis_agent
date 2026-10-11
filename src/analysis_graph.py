import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

def create_takuchi_boxplots(CSV_PATH, output_image_path):
    """
    不動産取引データのCSVを読み込み、外れ値を除外した上で
    都市計画別・建物構造別の単価の箱ひげ図を作成して保存・表示する関数
    
    Parameters:
    CSV_PATH (str): 読み込むCSVファイルのパス
    output_image_path (str): 出力する画像ファイルの保存先パス
    """
    
    # =====================================================================
    # データ読み込みと前処理
    # =====================================================================
    df = pd.read_csv(CSV_PATH, encoding='cp932')
    df['面積（㎡）'] = pd.to_numeric(df['面積（㎡）'], errors='coerce')

    # --- 1. 単価（㎡）列がない場合の作成例（既にある場合は不要） ---
    df['単価（㎡）'] = df['取引価格（総額）'] / df['面積（㎡）']

    # --- 2. IQR法による外れ値の算出 ---
    Q1 = df['単価（㎡）'].quantile(0.25)
    Q3 = df['単価（㎡）'].quantile(0.75)
    IQR = Q3 - Q1

    # 適正範囲の定義（1.5倍ルール）
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # 外れ値を除外したデータフレームを作成
    df_clean = df[(df['単価（㎡）'] >= lower_bound) & (df['単価（㎡）'] <= upper_bound)].copy()
    df = df_clean.copy()

    # 時期データの変換・フィルタリング・ソート
    quar_str = df['取引時期'].str.replace('年第', 'Q').str.replace('四半期', '')
    df['sort_key'] = pd.PeriodIndex(quar_str, freq='Q')
    idx = df['sort_key'] >= '2010Q1'
    df = df.loc[idx].copy()
    df.sort_values('sort_key', inplace=True)

    # =====================================================================
    # グラフの描画設定
    # =====================================================================
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))

    # 1. 都市計画でグルーピング
    sns.boxplot(
        data=df,
        x='sort_key',
        y='単価（㎡）',
        hue='都市計画',
        showfliers=False,  # 外れ値を非表示にして箱を大きく見せたい場合は True を False に変更
        ax=axes[0]
    )
    axes[0].set_title('都市計画別の取引価格（平均）')
    axes[0].tick_params(axis='x', rotation=45)

    # 2. 建物の構造でグルーピング
    sns.boxplot(
        data=df,
        x='sort_key',
        y='単価（㎡）',
        hue='建物の構造',
        showfliers=False,  # 外れ値を非表示にして箱を大きく見せたい場合は True を False に変更
        ax=axes[1]
    )
    axes[1].set_title('建物の構造別の取引価格（平均）')
    axes[1].tick_params(axis='x', rotation=45)

    # レイアウト調整と保存・表示
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    #plt.show()

def create_takuchi_lineplots(CSV_PATH, output_image_path):
    """
    不動産取引データのCSVを読み込み、外れ値を除外した上で
    都市計画別・建物構造別の単価の箱ひげ図を作成して保存・表示する関数
    
    Parameters:
    CSV_PATH (str): 読み込むCSVファイルのパス
    output_image_path (str): 出力する画像ファイルの保存先パス
    """
    
    # =====================================================================
    # データ読み込みと前処理
    # =====================================================================
    df = pd.read_csv(CSV_PATH, encoding='cp932')
    df['面積（㎡）'] = pd.to_numeric(df['面積（㎡）'], errors='coerce')

    # --- 1. 単価（㎡）列がない場合の作成例（既にある場合は不要） ---
    df['単価（㎡）'] = df['取引価格（総額）'] / df['面積（㎡）']

    # --- 2. IQR法による外れ値の算出 ---
    Q1 = df['単価（㎡）'].quantile(0.25)
    Q3 = df['単価（㎡）'].quantile(0.75)
    IQR = Q3 - Q1

    # 適正範囲の定義（1.5倍ルール）
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # 外れ値を除外したデータフレームを作成
    df_clean = df[(df['単価（㎡）'] >= lower_bound) & (df['単価（㎡）'] <= upper_bound)].copy()
    df = df_clean.copy()

    # 時期データの変換・フィルタリング・ソート
    quar_str = df['取引時期'].str.replace('年第', 'Q').str.replace('四半期', '')
    df['sort_key'] = pd.PeriodIndex(quar_str, freq='Q')
    idx = df['sort_key'] >= '2010Q1'
    df = df.loc[idx].copy()
    df.sort_values('sort_key', inplace=True)

    # =====================================================================
    # グラフの描画設定
    # =====================================================================
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))

    # 1. 都市計画でグルーピング
    sns.lineplot(
        data=df,
        x='取引時期',
        y='単価（㎡）',
        hue='都市計画',  # または '都市計画'
        marker='o',       # データ点に丸印を表示
        errorbar=None,     # 信頼区間（影）を非表示にして平均値の線のみにする
        ax=axes[0]
    )
    axes[0].set_title('都市計画別の取引価格（平均）')
    axes[0].tick_params(axis='x', rotation=45)
    
    # 2. 建物の構造でグルーピング
    sns.lineplot(
        data=df,
        x='取引時期',
        y='単価（㎡）',
        hue='建物の構造',  # または '都市計画'
        marker='o',       # データ点に丸印を表示
        errorbar=None,     # 信頼区間（影）を非表示にして平均値の線のみにする
        ax=axes[1]
    )
    axes[1].set_title('建物の構造別の取引価格（平均）')
    axes[1].tick_params(axis='x', rotation=45)

    # レイアウト調整と保存・表示
    plt.tight_layout()
    plt.savefig(output_image_path, dpi=300)
    #plt.show()
