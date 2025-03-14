# ZKP In CardGames
This is my final project of the lecture "Cryptography Engineering".

I invented a Zero-Knowledge Proof Protocol for Randomized Card Games: A cryptographic protocol enabling secure, verifiable, and privacy-preserving card shuffling and deal verification without revealing card identities. Belows are the descriptions in Chinese.

## 排堆加密
- 遊戲開始時，玩家 $A$ 和 $B$ 需要分別決定各自的 Private Permutation $P_A$ 與 $P_B$，皆為 $1$ 到 $n$ 的排列。兩位玩家將各自的 $P = {P_1, P_2, P_3, ... P_n}$ 透過以下方法加密:

- 公有參數 $N$ = 某個大質數 
- $S = \set{S_1, S_2, ... S_n}$ 為雙方事先同意的映射集，其中每個元素皆為模 $N$ 下的相異乘法 Generator

1. $g_i = S_{P_i}$ 將 $P_i$ 映射成一個 $N$ 的乘法 Generator
2. 玩家對每個 $i$ 決定一個Private Key $R_i$, 並定義 Public Key $U_i = g_i^{{R}_i} \mod N$
3. 將 $U = U_1, U_2, ... U_n$ 整個陣列傳給對手，作為初始排堆的承諾。 

## 零知識證明

### 單張卡牌是 $x$
- 玩家想向對手證明 $P_i = x$
- 等價於證明「知道某個 $R_i$ 能使 $U_i = S_{x}^{R_i} \mod N$成立」
- 當然可以直接攤牌證(公布 $R_i$)，但為了當作接下來的OR證明暖身，這邊使用零知識證明(不洩漏$R_i$)。
1. 證明人生成隨機數字 $c \in [0,N-1]$ ，計算 $C = g_i^c \mod N$ 並交出承諾 $C$
2. 驗整人提出任意挑戰 $b \in [0,N-1]$ ，要求證明人回答一個 $r$ 滿足 $S_{x}^r \equiv C * U_i^b \mod N$
3. 證明人回復 $r = c + b * R_i$ ， 驗證人確認其合法。
- 證明的可信度來自於「證明人無法事先預測挑戰 $b$」，因 $b$ 有 $N-1$ 種可能性。
- 證明人如果能事先知道 $b$，他可以將 $C$ 設成  $C = \frac{S_{x}^c}{U_i ^ b} \mod N$ (把Public key 的部分事先扣掉)，後續回復 $r = c$ 即可過關。這樣一來，即使當初設定 $U_i$ 的 $g_i$ 並不是 $S_{x}$，驗證者也不會發現。
 
### 多張卡片中有一張是 $x$
- 假設被詢問的集合是 $Q = {Q_1, Q_2,...Q_m}$
- 玩家想向對手證明 $\exists i \in Q, P_i = x$
- 等價於證明「 $\exists i \in Q$, 知道某個 $R_i$ 能使 $U_i = S_{x}^{R_i} \mod N$ 成立」
- 問題轉換成多個ZKP系統，要證明至少知道其中一個知識，且不洩漏是知道其中哪一個。

#### 整體流程
1. 證明人提交承諾 $C_{Q_1}, C_{Q_2},...C_{Q_m}$ 
2. 驗證人提出挑戰 $b_{sum} \in [0, N-1]$
3. 證明人自由分配額度 $b_{Q_1}, b_{Q_2},...b_{Q_m}$ 使得其總合模 $N-1$ 為 $b_{sum}$
4. 證明人提出 $r_{Q_1}, r_{Q_2},...r_{Q_m}$ 以及分配 $b_{sum}$ 的方法 $b_{Q_1}, b_{Q_2},...b_{Q_m}$
5. 驗證人檢查 $b_{Q_1}+b_{Q_2}+...+b_{Q_m}=b_{sum} \mod N-1$ 且 $S_{x}^{r_i} \equiv C_i * U_i^{b_i} \mod N$ 對所有 $i \in Q$ 皆符合

#### 證明人詳細過程

- 假設玩家的 $P_j = x, j \in Q$，代表玩家知道 $U_j = S_{x}^{R_j} \mod N$ 之 $R_j$解，但不知道其他 $i \neq j, i \in Q$ 的 $U_i = S_{x}^{R_i} \mod N$ 之 $R_i$ 解
- 在步驟1的時候，可以對每個 $i \neq j, i \in Q$ 事先預訂一個任意的 $b_i$ ， 再透過上述「事先知道 $b$ ，偽造證明的方法」事先算出對應的 $(b_i, C_i, r_i)$ ($C_i = \frac{S_{x}^{r_i}}{U_i ^ b} \mod N$)
- 至於 $c_j$ 與 $C_j$ 則是按照正常的方法生成 ($C_j = g_j^{c_j} \mod N$)
- 不管 $b_{sum}$ 為任何值，都可以把 $b_j$ 設成 $b_{sum} - \sum_{i \neq j, i \in Q}{b_i} \mod N-1$ 滿足總和限制
- 再用對應的 $b_j$ 用原本方法算 $r_j$ 即可 ($r_j = c_j + b_j * R_j$)。

#### 正確性

- 若玩家知道至少一個知識，那他一定能通過這個ZKP測驗。在限定 $b_{sum}$ 的總和下他有 $m-1$ 個自由度能夠分配其餘的 $b_i$，剩下只需要完成原本的「給對手任意決定的 $b_j$ 的測驗」
- 若玩家一個知識都沒有掌握，那他至少需要解出其中一個 discrete logarithm problem，然而這不可能 (NP-Hard)
- 驗證者只能驗證，不能回推任何的 Private Key，也不能知道證明人知道的是哪一個知識，因為在他眼中，所有 $C$ 、 $r$ 、 $b$ 都是 $[0,N-1]$ 的隨機數。

## 能達成的功能

我們已經說明了能達成詢問: $Query(x, Q = \set{Q_1, Q_2, ... Q_m})$
要求某個玩家證明 $P_{Q_1}, P_{Q_2}, ... P_{Q_m}$ 其中一個為 $x$

### 證明初始排堆是 $[1,n]$ 的排列
- 問題等價於 $1,2,...,n$ 都至少出現一次
- 可以對每一個 $1 \leq i \leq n$ 都證明 $Query(i,\set{1,2,...,n})$
### 證明卡片子集 $Q$ 中有一張是 $x$
- 即證明 $Query(x, Q)$
### 證明卡片子集 $Q$ 中沒有一張是 $x$
- 等價於證明 $Query(x, Q')$， $Q'$ 是 $Q$ 的補集。

### (擴展) 洗牌、手牌系統
假設輪到 $A$ 抽牌:
每回合由對手 $B$ 指定一個 $index$，該回合玩家抽出 $P_{index}$ ，放入手牌。
- 由於 $B$ 不知道 $A$ 會怎麼排序 Permutation， $A$ 也不知道 $B$ 會指定哪一個 $index$ ，所以整個過程可以視為隨機抽牌，也就是洗牌過了。 
- 在此情景下， $B$ 可以記錄至今的回合指定哪些 $index$ ，這個集合就是象徵了手牌的概念。後續也可以針對這個集合去做猜牌的動作
