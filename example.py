from random import randrange
import time
n = 5
N = 10 ** 9 + 7
s = []

sleep_time = 0.4
def check_generator(x, p):
    # check if x is a multiplicative generator of p, where p is a prime
    # works only when (p-1)/2 is also a prime
    d = (p - 1) // 2
    return pow(x, d, p) != 1

def init_generaters():
    global s
    s = []
    i = 1
    while len(s) < n:
        if check_generator(i, N): s.append(i)
        i = i + 1

def generate_public_key (private_permutation, private_keys):
    pu = []
    for i in range(n):
        pu.append(pow(s[private_permutation[i]], private_keys[i], N))
    return pu

class Prover:
    def __init__(self, private_permutation, private_keys, public_keys):
        self.P = private_permutation
        self.R = private_keys
        self.U = public_keys
    def get_public(self):
        return self.U
    def init_query(self, Q, x):
        self.Q = Q
        self.x = x
    def generate_commit(self):
        self.j = -1
        self.c, self.C, self.b = [], [], []
        for i in range(n):
            if self.P[i] == self.x:
                self.j = i
        if self.j in self.Q:
            self.reply = 1
        else:
            self.reply = 0
            invQ = []
            for i in range(n):
                if i not in self.Q: invQ.append(i)
            self.Q = invQ
        for i in self.Q:
            if i == self.j:
                _c = randrange(N - 1)
                _C = pow(s[self.x], _c, N)
                self.c.append(_c)
                self.C.append(_C)
                self.b.append(-1)
            else:
                _b = randrange(N - 1)
                _c = randrange(N - 1)
                _C = pow(s[self.x], _c, N) * pow(self.U[i], _b * (N - 2) % (N - 1), N) % N
                self.c.append(_c)
                self.C.append(_C)
                self.b.append(_b)
        return self.reply, self.C
    def reply_challenge(self, b_sum):
        b_j = b_sum
        r = []
        for i in range(len(self.Q)):
            if self.Q[i] != self.j:
                b_j -= self.b[i]
                if b_j < 0: b_j += N - 1
        for i in range(len(self.Q)):
            if self.Q[i] == self.j:
                self.b[i] = b_j
                r.append((self.c[i] + self.b[i] * self.R[self.Q[i]]) % (N - 1))
            else:
                r.append(self.c[i])
        return self.b, r

def Verify(prover, Q, x): # x in Q : 1, x not in Q: 0, invalid proof: -1
    U = prover.get_public()
    prover.init_query(Q, x)
    result, C = prover.generate_commit()
    if not result:
        invQ = []
        for i in range(n):
            if i not in Q: invQ.append(i)
        Q = invQ
    if len(Q) != len(C):
        print('Invalid proof.')
        return -1
    time.sleep(sleep_time)
    print('Initial commit: ', ('X is in Q,' if result else 'X is not in Q,'), 'C =', C)
    b_sum = int(input('Enter challenge between [0, N-2], or -1 for a random one: '))
    if b_sum == -1:
        b_sum = randrange(N - 1)
        time.sleep(sleep_time)
        print('Challenge =', b_sum)
    b, r = prover.reply_challenge(b_sum)
    if len(Q) != len(b) or len(Q) != len(r):
        print('Invalid proof.')
        return -1
    time.sleep(sleep_time)
    print('Prover\'s reply r =', r, 'b =', b, '\n')
    sum = 0
    for i in range(len(Q)):
        if C[i] < 0 or b[i] < 0 or r[i] < 0 or C[i] >= N or b[i] >= N - 1 or r[i] >= N - 1:
            print('Invalid proof.')
            return -1
        temp1 = pow(s[x], r[i], N)
        temp2 = C[i] * pow(U[Q[i]], b[i], N) % N
        time.sleep(sleep_time)
        print('Verifying for index %d... U = %d, (C, r, b) = (%d, %d, %d)' %(Q[i], U[Q[i]], C[i], r[i], b[i]))
        time.sleep(sleep_time)
        print('S_x = %d; S_x ^ r (mod N) = %d, C * U ^ b (mod N) = %d' %(s[x], temp1, temp2))
        if temp1 != temp2:
            print('Invalid proof.')
            return -1
        sum += b[i]
        time.sleep(sleep_time)
        print('Index %d verified: Valid proof.\n' % (Q[i]))
        time.sleep(sleep_time)
    if sum % (N - 1) != b_sum:
        print('Invalid proof.')
        return -1
    time.sleep(sleep_time)
    print('Sum of b\'s mod N - 1:', sum % (N - 1), ', Challenge =', b_sum, '\n')
    time.sleep(sleep_time)
    print('Result: Valid proof.')
    return result
def test():
    global n, N, s
    print("Setting global parameters...")
    n = int(input('Enter the size of the deck n: '))
    _N = int(input('Enter the prime modulo N, or -1 to leave it as default (10^9+7): '))
    if _N != -1: N = _N
    else: N = 10 ** 9 + 7
    s = list(map(int, input('Enter the generator map, or enter single -1 to generate a arbitrary one: ').split()))
    if s[0] == -1:
        init_generaters()
    print("Setting private parameters...")
    P = list(map(int, input('Enter the private permutation. It should be 0-based and seperated by spaces, eg. \'3 0 2 1\': ').split()))
    if len(P) != n:
        print('Error: Deck size not consistent. Deck size should be ', n, 'but found', len(P))
        return
    R = list(map(int, input('Enter the private keys, or enter single -1 to generate a random set: ').split()))
    if R[0] == -1: R = [randrange(N) for i in range(n)]
    if len(R) != n:
        print('Error: Private keys size not consistent. Deck size should be ', n, 'but found', len(R))
        return
    U = generate_public_key(P, R)
    prover = Prover(P, R, U)
    print('Public keys automatically generated.')
    def check_status():
        time.sleep(sleep_time)
        print('Checking status...')
        time.sleep(sleep_time)
        print('Modulo N: ', N)
        time.sleep(sleep_time)
        print('Generator set S: ', s)
        time.sleep(sleep_time)
        print('Private permutation H: ', P)
        time.sleep(sleep_time)
        print('Private keys R: ', R)
        time.sleep(sleep_time)
        print('Public keys U: ', U)
        time.sleep(sleep_time)
    check_status()
    while True:
        operation = int(input('Enter 0 to check current status, 1 to perform query, and -1 to reset: '))
        if operation == -1:
            print('Test completed successfully.')
            return
        elif operation == 0:
            check_status()
        elif operation == 1:
            Q = list(map(int, input('Enter a subset of indices, 0-based and separated by spaces, eg. \'0 2\': ').split()))
            Q.sort()
            x = int(input('Enter the target integer x between [0, n-1]: '))
            result = Verify(prover, Q, x)
            time.sleep(sleep_time)
            if result == 1: print('Successfully proved x is in Q.\n')
            elif result == 0: print('Successfully proved x is not in Q.\n')
            else: print('x is not in the initial deck.\n')
# Local test
while True:
    test()