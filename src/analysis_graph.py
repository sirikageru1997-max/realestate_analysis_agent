import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 日本語フォントの設定（OS環境に合わせて変更してください。Google Colabの場合は 'IPAGothic' 等をインストールして指定します）
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']


def create_real_estate_scatter_plot(csv_file_path, output_image_path="scatter_plot.png"):
    """
    不動産データのCSVファイルを読み込み、家賃と専有面積の散布図を作成して保存する関数。

    Args:
        csv_file_path (str): 入力となるCSVファイルのパス
        output_image_path (str, optional): 出力する画像ファイルのパス. デフォルトは "scatter_plot.png".
    """
    try:
        # 1. CSVデータの読み込み
        # データの構造が '候補', '時間', '築年数', '駅', '構造', '階層', '家賃(万)', '専有面積(m2)', ... のようになっていると仮定
        # 必要に応じて、ヘッダーの有無や列名を指定してください
        df = pd.read_csv(csv_file_path)

        # 2. 必要な列の抽出とデータクリーニング
        # ここでは、列名が '家賃' と '専有面積' に似たものを含んでいると仮定しています。
        # 実際のCSVの列名に合わせて変更してください。
        # 例: df = pd.read_csv(csv_file_path, header=None, names=['A', 'B', 'C', 'D', 'E', 'F', 'Rent', 'Area', ...])
        
        # 仮の処理: 7列目が家賃(万)、8列目が面積(m2)の場合
        if len(df.columns) >= 8:
             rent_col = df.columns[6]
             area_col = df.columns[7]
        else:
             print("エラー: CSVの列数が不足しています。")
             return
        
        # 数値データに変換（エラーとなる文字列はNaNにし、その後除外する）
        df['Rent_num'] = pd.to_numeric(df[rent_col], errors='coerce')
        df['Area_num'] = pd.to_numeric(df[area_col], errors='coerce')
        
        # NaNを含む行を削除
        df_clean = df.dropna(subset=['Rent_num', 'Area_num'])

        if df_clean.empty:
            print("エラー: グラフにプロットできる有効な数値データがありません。")
            return

        # 3. グラフの作成
        plt.figure(figsize=(10, 6))
        plt.scatter(df_clean['Area_num'], df_clean['Rent_num'], color='blue', alpha=0.7)

        # 4. グラフの装飾
        plt.title('祖師ヶ谷大蔵周辺 物件の専有面積と家賃の関係', fontsize=16)
        plt.xlabel('専有面積 (m²)', fontsize=14)
        plt.ylabel('家賃 (万円)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        
        # 5. グラフの保存と表示
        plt.tight_layout()
        plt.savefig(output_image_path, dpi=300)
        plt.show()
        
        print(f"散布図を作成し、{output_image_path} に保存しました。")

    except FileNotFoundError:
        print(f"エラー: ファイル '{csv_file_path}' が見つかりません。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

# ==========================================
# 使用例
# ==========================================
# csv_file_path = "path/to/your/Odakyu-Odawara line_Soshigaya Okura_20053_20261.csv"
# create_real_estate_scatter_plot(csv_file_path)
