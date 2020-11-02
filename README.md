# Data Mining 1091 - Project 1

## Association Rule
補充 1

1. Kaggle 和 IBM 兩個資料集都需要實做，Kaggle資料集請自行尋找
2. 需實做 Aprior Algorithm 以及 FP-growth 兩種演算法，Hash 和 Tree 可自行決定是否實做
3. 作業除了程式碼以外需要繳交一份報告來簡短闡述程式碼以及一些心得和研究

補充 2
1. 需要至少實做兩個Dataset
2. 需要實做 Aprior Algorithm 和 FP-growth 兩種演算法
3. 輸出結果需包含 Frequent Patterns 和 Rules
4. 需要繳交分析報告

# 前置作業

## 系統說明

| 欄位 | 說明
| -------- | -------- |
| 作業系統     | Linux 5.4.72-1-MANJARO     |
| Architecture | x86_64 |
| CPU | Intel i7-1065G7 |
| RAM | 16GB |

## 資料集

### Kaggle: [Market Basket Optimzation](https://www.kaggle.com/roshansharma/market-basket-optimization)

| 欄位 | 數目 |
| -------- | -------- |
| Transactions     | 7501     |
| Unique items | 120 |
| Avearge itemset length | 3.9 ~= 4 |


### IBM Dataset: [Tool](https://github.com/halfvim/quest)

爲了保持資料的一致性，所以在產生 Random Data 希望能與 Kaggle Data 的資料大小與 Dimension 一樣。

**產生資料辦法如下：**

* 首先，需要先安裝 IBM Quest Synthetic Data Generator （使用 Linux 需自行安裝，用 Windows 則可以使用 `.exe` 當）。
* 根據上述參數執行 Generator。
    ```=
    ./gen lit -ascii \
    -ntrans 7.5 \
    -tlen 4 \
    -nitems 0.12 \ 
    -fname output
    ```
    *ntrans* —> Number of transaction， 以千爲單位。
    *tlen* -> transaction length, 平均一筆 Transaction 要有幾個 Item。
    *nitems* -> Item 總數是多少個，以千爲單位。
* 完成資料生成後，需將資料轉成演算法可以執行的格式。

### 簡易測資（基本格式）

驗證關聯法則演算法所用資料
```=python
data = [
    ['A', 'C', 'D'],
    ['B', 'C', 'E'],
    ['A', 'B', 'C', 'E'],
    ['B', 'E']
]
```

資料格式是 **List of List**

## 建設 WEKA Associator

網路上相關套件不多，有的套件只有對 Frequent Data Set 做 API, 而 WEKA 則有完整的 API + 產生 Rules 的工具。

### 安裝

**Python3 Wrapper**  [Here](https://github.com/fracpete/python-weka-wrapper3)
```
Python wrapper for the Java machine learning workbench Weka using the javabridge library.

Requirements:
    Python 3 (for Python 2.7 version see here)
    javabridge (>= 1.0.14)
    matplotlib (optional)
    pygraphviz (optional)
    PIL (optional)
    Oracle JDK 1.8+

Uses:
    Weka (3.9.4)

```

### Weka 資料格式

**說明：**
在 Weka 上使用的資料需要符合 `ARFF` 檔案格式，需要定義各個欄位與 Relation，資料以 Data Frame 的格式記錄，不管在 Testing Data、Market Basket Optimization 等資料集，都需要將資料轉換成 `ARFF` 檔案讓 Weka 使用。

**以測試資料轉換 `ARFF` 爲例：**

Testing data:
```=python
data = [
    ['A', 'C', 'D'],
    ['B', 'C', 'E'],
    ['A', 'B', 'C', 'E'],
    ['B', 'E']
]
```
In arff format:
```=arff
@relation 'value'

@attribute A, {'1'}
@attribute B, {'1'}
@attribute C, {'1'}
@attribute D, {'1'}
@attribute E, {'1'}

@data
'1', ?, '1', '1', ?
?, '1', '1', ?, '1'
'1', '1', '1', ?, '1'
?, '1', ?, ?, '1'
```

實質上是將資料做 **Encoding**

## 實驗結果

實驗結果請參照：`analysis.ipynb` or [WebView Note](https://nbviewer.jupyter.org/github/iknowright/data-mining-association-rules/blob/master/analysis.ipynb)

## 心得

**演算法部分：** 在短時間需要完成兩個演算法是非常苦難的，所以研究網路上的資源變成此作業的一個很重要的環節，不僅自身要先對兩個演算法內容有一定瞭解，再來就是 Trace 他人的程式碼，對比程式邏輯是否正確，經過一些簡單的測試後再套入 Kaggle 與 IBM generator 的資料，來驗證程式的可執行性。開發上，分別對 Apriori Algorithm 與 FP-growth 各自進行基本資料的測試，測試成功後，再將所有資料與程式模組化，將其呈現。

**資料的轉換：** 在此 Project 設計了三組測試資料，分別是 Sample Data(`list`), Kaggle(`csv`), 與 IBM(just `txt`)，三者在原本的資料形態多不相同。因爲要迎合演算法吃進來的格式，必須將其他資料形態轉爲最簡單的 `list` 格式給 Function 使用。另外 Weka 套件所使用的資料格式 (`.arff`) 則與 Project Associator 所使用的格式 (`list` of `list`) 相差甚遠，並且需要做 `Encoding` 轉換才能使用。所以在資料的格式轉換則需要另外下功夫。

**重構程式：** 將演算法、資料集、與輸出結果做資料夾管理，也將程式執行參數化，只需要註明 `command line argument` 即可。


### 參考文獻

1. [一步步教你輕鬆學關聯規則Apriori演算法](https://www.itread01.com/content/1544958735.html)
2. [FP-growth 算法与Python实现](https://blog.csdn.net/songbinxu/article/details/80411388)