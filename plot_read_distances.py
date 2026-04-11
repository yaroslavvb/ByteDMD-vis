#!/usr/bin/env python3
"""Plot per-read LRU stack depth over time for the major ByteDMD algorithms.

For each algorithm we collect the trace (list of read depths, one per tracked
read, in execution order) via bytedmd.traced_eval and plot it as a line chart:
x = read index, y = stack depth at that read. Output PNGs land next to this
script in visualizations/.

Also produces a combined plot comparing recursive (block) matmul vs Strassen
under a "cost over time" view: y = cumulative sum of ceil(sqrt(depth)).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from bytedmd import traced_eval

OUT_DIR = os.path.dirname(__file__)


# ---------- algorithms ----------

def matvec(A, x):
    n = len(x)
    y = [None] * n
    for i in range(n):
        s = A[i][0] * x[0]
        for j in range(1, n):
            s = s + A[i][j] * x[j]
        y[i] = s
    return y


def vecmat(A, x):
    n = len(x)
    y = [None] * n
    for j in range(n):
        s = x[0] * A[0][j]
        for i in range(1, n):
            s = s + x[i] * A[i][j]
        y[j] = s
    return y


def matmul_ijk(A, B):
    n = len(A)
    C = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = A[i][0] * B[0][j]
            for k in range(1, n):
                s = s + A[i][k] * B[k][j]
            C[i][j] = s
    return C


def matmul_snake(A, B):
    n = len(A)
    C = [[None] * n for _ in range(n)]
    for i in range(n):
        js = range(n) if i % 2 == 0 else range(n - 1, -1, -1)
        for j in js:
            s = A[i][0] * B[0][j]
            for k in range(1, n):
                s = s + A[i][k] * B[k][j]
            C[i][j] = s
    return C


def _add_mat(X, Y):
    return [[X[i][j] + Y[i][j] for j in range(len(X))] for i in range(len(X))]


def _sub_mat(X, Y):
    return [[X[i][j] - Y[i][j] for j in range(len(X))] for i in range(len(X))]


def matmul_recursive(A, B):
    """Divide-and-conquer block matmul without reuse (the Gemini algorithm)."""
    n = len(A)
    if n == 1:
        return [[A[0][0] * B[0][0]]]
    m = n // 2
    A11 = [r[:m] for r in A[:m]]; A12 = [r[m:] for r in A[:m]]
    A21 = [r[:m] for r in A[m:]]; A22 = [r[m:] for r in A[m:]]
    B11 = [r[:m] for r in B[:m]]; B12 = [r[m:] for r in B[:m]]
    B21 = [r[:m] for r in B[m:]]; B22 = [r[m:] for r in B[m:]]
    C11 = _add_mat(matmul_recursive(A11, B11), matmul_recursive(A12, B21))
    C12 = _add_mat(matmul_recursive(A11, B12), matmul_recursive(A12, B22))
    C21 = _add_mat(matmul_recursive(A21, B11), matmul_recursive(A22, B21))
    C22 = _add_mat(matmul_recursive(A21, B12), matmul_recursive(A22, B22))
    C = []
    for i in range(m): C.append(C11[i] + C12[i])
    for i in range(m): C.append(C21[i] + C22[i])
    return C


def matmul_strassen(A, B):
    n = len(A)
    if n == 1:
        return [[A[0][0] * B[0][0]]]
    m = n // 2
    A11 = [r[:m] for r in A[:m]]; A12 = [r[m:] for r in A[:m]]
    A21 = [r[:m] for r in A[m:]]; A22 = [r[m:] for r in A[m:]]
    B11 = [r[:m] for r in B[:m]]; B12 = [r[m:] for r in B[:m]]
    B21 = [r[:m] for r in B[m:]]; B22 = [r[m:] for r in B[m:]]
    M1 = matmul_strassen(_add_mat(A11, A22), _add_mat(B11, B22))
    M2 = matmul_strassen(_add_mat(A21, A22), B11)
    M3 = matmul_strassen(A11, _sub_mat(B12, B22))
    M4 = matmul_strassen(A22, _sub_mat(B21, B11))
    M5 = matmul_strassen(_add_mat(A11, A12), B22)
    M6 = matmul_strassen(_sub_mat(A21, A11), _add_mat(B11, B12))
    M7 = matmul_strassen(_sub_mat(A12, A22), _add_mat(B21, B22))
    C11 = _add_mat(_sub_mat(_add_mat(M1, M4), M5), M7)
    C12 = _add_mat(M3, M5)
    C21 = _add_mat(M2, M4)
    C22 = _add_mat(_sub_mat(_add_mat(M1, M3), M2), M6)
    C = []
    for i in range(m): C.append(C11[i] + C12[i])
    for i in range(m): C.append(C21[i] + C22[i])
    return C


# Flash attention (small, self-contained; mirrors benchmarks/benchmark_attention.py)
def _max2(a, b):
    d = a - b
    return a if d > 0 else b


def naive_attention(Q, K, V):
    N = len(Q)
    d = len(Q[0])
    # scores = Q @ K^T
    S = [[sum(Q[i][t] * K[j][t] for t in range(d)) for j in range(N)] for i in range(N)]
    # row softmax
    P = []
    for i in range(N):
        m = S[i][0]
        for j in range(1, N):
            m = _max2(m, S[i][j])
        exps = [(S[i][j] - m) * (S[i][j] - m) + 1 for j in range(N)]  # placeholder exp
        Z = exps[0]
        for j in range(1, N):
            Z = Z + exps[j]
        P.append([exps[j] * (1 / Z) for j in range(N)])
    # O = P @ V
    O = [[sum(P[i][j] * V[j][t] for j in range(N)) for t in range(d)] for i in range(N)]
    return O


def flash_attention(Q, K, V, Bk=2):
    """Online-softmax block version. Bk = key block size."""
    N = len(Q)
    d = len(Q[0])
    O = [[Q[0][0] * 0 for _ in range(d)] for _ in range(N)]
    for i in range(N):
        m_i = None
        l_i = None
        O_i = [Q[0][0] * 0 for _ in range(d)]
        for j0 in range(0, N, Bk):
            j1 = min(j0 + Bk, N)
            # scores for the block
            s = [sum(Q[i][t] * K[j][t] for t in range(d)) for j in range(j0, j1)]
            m_block = s[0]
            for v in s[1:]:
                m_block = _max2(m_block, v)
            if m_i is None:
                m_new = m_block
            else:
                m_new = _max2(m_i, m_block)
            # placeholder "exp": use square-plus-one to stay tracked and positive
            p = [(v - m_new) * (v - m_new) + 1 for v in s]
            l_block = p[0]
            for v in p[1:]:
                l_block = l_block + v
            if l_i is None:
                l_new = l_block
                for t in range(d):
                    acc = p[0] * V[j0][t]
                    for jj in range(1, j1 - j0):
                        acc = acc + p[jj] * V[j0 + jj][t]
                    O_i[t] = acc
            else:
                # rescale + accumulate (simplified)
                scale_old = (m_i - m_new) * (m_i - m_new) + 1
                l_new = l_i * scale_old + l_block
                for t in range(d):
                    acc = O_i[t] * scale_old
                    for jj in range(j1 - j0):
                        acc = acc + p[jj] * V[j0 + jj][t]
                    O_i[t] = acc
            m_i = m_new
            l_i = l_new
        inv = 1 / l_i
        for t in range(d):
            O[i][t] = O_i[t] * inv
    return O


# ---------- plotting helpers ----------

def trace_of(func, args):
    trace, _ = traced_eval(func, args)
    return trace


def plot_sizes(title, filename, func, make_args, sizes, ncols=2, ylabel='stack depth'):
    """One figure, subplot per size, line = depth vs read index."""
    nrows = math.ceil(len(sizes) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.5 * ncols, 3.0 * nrows),
                             squeeze=False)
    for ax, n in zip(axes.flat, sizes):
        trace = trace_of(func, make_args(n))
        ax.plot(range(len(trace)), trace, linewidth=0.7)
        total = sum(math.isqrt(d - 1) + 1 for d in trace) if trace else 0
        ax.set_title(f'N={n}  (reads={len(trace)}, cost={total})', fontsize=10)
        ax.set_xlabel('read index')
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
    for ax in axes.flat[len(sizes):]:
        ax.axis('off')
    fig.suptitle(title, fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f'wrote {path}')


def plot_depths_over_time(title, filename, series, kind='line'):
    """series: list of (label, trace). Plot raw read depth vs read index.

    kind='line' draws line plots; kind='bar' overlays bar charts (one bar per
    read, thin, semi-transparent) which is easier to read when the signal is
    spiky and you want to compare two traces that frequently cross.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    if kind == 'bar':
        colors = ['#1f77b4', '#d62728', '#2ca02c', '#ff7f0e']
        for (label, trace), color in zip(series, colors):
            xs = range(len(trace))
            ax.bar(xs, trace, width=1.0, align='edge', color=color, alpha=0.55,
                   edgecolor='none',
                   label=f'{label} (reads={len(trace)}, max={max(trace) if trace else 0})')
    else:
        for label, trace in series:
            ax.plot(range(len(trace)), trace,
                    label=f'{label} (reads={len(trace)}, max={max(trace) if trace else 0})',
                    linewidth=0.7, alpha=0.85)
    ax.set_xlabel('read index')
    ax.set_ylabel('stack depth')
    ax.set_title(title)
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f'wrote {path}')


def plot_costs_over_time(title, filename, series):
    """series: list of (label, trace). Plot cumulative ceil(sqrt(d))."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, trace in series:
        cum = np.cumsum([math.isqrt(d - 1) + 1 for d in trace])
        ax.plot(range(len(cum)), cum, label=f'{label} (final={int(cum[-1]) if len(cum) else 0})',
                linewidth=1.2)
    ax.set_xlabel('read index')
    ax.set_ylabel('cumulative ByteDMD cost')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=120)
    plt.close(fig)
    print(f'wrote {path}')


# ---------- argument factories ----------

def ones_matvec(n):
    return (np.ones((n, n)), np.ones(n))


def ones_matmul(n):
    return (np.ones((n, n)), np.ones((n, n)))


def ones_attention(n, d=4):
    return (np.ones((n, d)), np.ones((n, d)), np.ones((n, d)))


# ---------- main ----------

def main():
    mv_sizes = [2, 4, 8, 16]
    mm_sizes = [2, 4, 8]
    rec_sizes = [2, 4, 8]            # power-of-two for Strassen/recursive
    att_sizes = [2, 4, 8]

    plot_sizes('matvec: read depth over time',
               'matvec_depth.png', matvec, ones_matvec, mv_sizes)
    plot_sizes('vecmat: read depth over time',
               'vecmat_depth.png', vecmat, ones_matvec, mv_sizes)
    plot_sizes('matmul (i-j-k): read depth over time',
               'matmul_ijk_depth.png', matmul_ijk, ones_matmul, mm_sizes)
    plot_sizes('matmul (snake-j): read depth over time',
               'matmul_snake_depth.png', matmul_snake, ones_matmul, mm_sizes)
    plot_sizes('recursive matmul: read depth over time',
               'matmul_recursive_depth.png', matmul_recursive, ones_matmul, rec_sizes)
    plot_sizes('Strassen matmul: read depth over time',
               'matmul_strassen_depth.png', matmul_strassen, ones_matmul, rec_sizes)
    plot_sizes('flash attention (Bk=2): read depth over time',
               'flash_attention_depth.png',
               lambda Q, K, V: flash_attention(Q, K, V, Bk=2),
               lambda n: ones_attention(n, d=4), att_sizes)
    plot_sizes('naive attention: read depth over time',
               'naive_attention_depth.png',
               naive_attention,
               lambda n: ones_attention(n, d=4), att_sizes)

    # Strassen vs recursive matmul: costs over time at N=8
    n_cmp = 8
    A = np.ones((n_cmp, n_cmp))
    B = np.ones((n_cmp, n_cmp))
    rec_trace = trace_of(matmul_recursive, (A, B))
    str_trace = trace_of(matmul_strassen, (A, B))
    plot_costs_over_time(
        f'Strassen vs recursive matmul: cumulative cost over time (N={n_cmp})',
        'strassen_vs_recursive_cost.png',
        [('recursive (block)', rec_trace), ('Strassen', str_trace)],
    )
    plot_depths_over_time(
        f'Strassen vs recursive matmul: read depth over time (N={n_cmp})',
        'strassen_vs_recursive_depth.png',
        [('recursive (block)', rec_trace), ('Strassen', str_trace)],
    )

    # matvec vs vecmat (auto-GC, since _Tracked.__del__ releases dead temps).
    n_mv = 8
    A = np.ones((n_mv, n_mv))
    x = np.ones(n_mv)
    mv_trace = trace_of(matvec, (A, x))
    vm_trace = trace_of(vecmat, (A, x))
    plot_depths_over_time(
        f'matvec vs vecmat: read depth over time, GC on (N={n_mv})',
        'matvec_vs_vecmat_depth.png',
        [('matvec (i-j)', mv_trace), ('vecmat (j-i)', vm_trace)],
        kind='bar',
    )

    # Naive i-j-k vs snake-j: depth over time on the same axes.
    n_snake = 8
    A = np.ones((n_snake, n_snake))
    B = np.ones((n_snake, n_snake))
    ijk_trace = trace_of(matmul_ijk, (A, B))
    snake_trace = trace_of(matmul_snake, (A, B))
    plot_depths_over_time(
        f'Naive vs snake-j matmul: read depth over time (N={n_snake})',
        'matmul_ijk_vs_snake_depth.png',
        [('i-j-k (naive)', ijk_trace), ('snake-j', snake_trace)],
    )


if __name__ == '__main__':
    main()
