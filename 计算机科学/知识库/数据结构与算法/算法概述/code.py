import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['STHeiti']
plt.rcParams['axes.unicode_minus'] = False

n = np.arange(1, 11, 1)  # 输入规模：1 到 10，步长 1

o1 = np.ones_like(n, dtype=float)
ologn = np.log(n)
on = n
onlogn = n * np.log(n)
on2 = n ** 2

plt.figure(figsize=(10, 6))
plt.plot(n, o1, label=r'$O(1)$ 常量', lw=2)
plt.plot(n, ologn, label=r'$O(\log n)$ 对数', lw=2)
plt.plot(n, on, label=r'$O(n)$ 线性', lw=2)
plt.plot(n, onlogn, label=r'$O(n\log n)$ 线性对数', lw=2)
plt.plot(n, on2, label=r'$O(n^2)$ 平方', lw=2)

plt.xlabel('输入规模 n')
plt.ylabel('运算代价')
plt.title('常见时间复杂度对比')
plt.legend()
plt.xlim(1, 10)
plt.ylim(1, 10)
plt.xticks(range(0, 11))
plt.yticks(range(0, 11))
plt.grid(True, alpha=0.3)
plt.show()
