#!/usr/bin/env python3
"""
Reproduction of the Shifter Network from PDP Vol 1, Chapter 8
"Learning Internal Representations by Error Propagation"
by Rumelhart, Hinton & Williams (1986).

The network learns to shift a binary input pattern left, right,
or not at all, based on a 3-unit one-hot shift command signal.

Architecture:
  - 8 input units (binary pattern)
  - 3 shift-command units (one-hot: shift-left, no-shift, shift-right)
  - Hidden layer (variable size, default 20 — as in the original)
  - 8 output units (the shifted pattern)

The original PDP experiment used:
  - Logistic (sigmoid) activation
  - Backpropagation with momentum
  - Random binary patterns with P(1) ≈ 0.5
  - Circular (wrap-around) shifting

This script trains the network and visualizes the learned internal
representations, reproducing the key findings from the book.
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# ─── Reproducibility ───
np.random.seed(42)


# ═══════════════════════════════════════════════════════════════
# NETWORK
# ═══════════════════════════════════════════════════════════════

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_deriv(a):
    """Derivative of sigmoid given its output a."""
    return a * (1.0 - a)


class ShifterNetwork:
    """
    Feedforward network: [8 input + 3 shift] → [hidden] → [8 output]
    Trained with backpropagation + momentum, as in PDP Chapter 8.
    """

    def __init__(self, n_input=8, n_shift=3, n_hidden=20, n_output=8,
                 lr=0.25, momentum=0.9, weight_range=0.5):
        self.n_input = n_input
        self.n_shift = n_shift
        self.n_hidden = n_hidden
        self.n_output = n_output
        self.lr = lr
        self.momentum = momentum

        n_in = n_input + n_shift  # 11 total input units

        # Small random initial weights as in PDP
        self.W1 = np.random.uniform(-weight_range, weight_range, (n_in, n_hidden))
        self.b1 = np.zeros(n_hidden)
        self.W2 = np.random.uniform(-weight_range, weight_range, (n_hidden, n_output))
        self.b2 = np.zeros(n_output)

        # Momentum buffers
        self.dW1_prev = np.zeros_like(self.W1)
        self.db1_prev = np.zeros_like(self.b1)
        self.dW2_prev = np.zeros_like(self.W2)
        self.db2_prev = np.zeros_like(self.b2)

    def forward(self, x):
        """Forward pass. x shape: (batch, 11)"""
        self.x = np.atleast_2d(x)
        self.h_net = self.x @ self.W1 + self.b1
        self.h = sigmoid(self.h_net)
        self.o_net = self.h @ self.W2 + self.b2
        self.o = sigmoid(self.o_net)
        return self.o

    def backward(self, target):
        """Backward pass + weight update with momentum."""
        batch_size = target.shape[0]

        # Output layer deltas
        error = target - self.o
        delta_o = error * sigmoid_deriv(self.o)

        # Hidden layer deltas (backpropagation)
        delta_h = (delta_o @ self.W2.T) * sigmoid_deriv(self.h)

        # Gradients
        dW2 = self.h.T @ delta_o / batch_size
        db2 = delta_o.mean(axis=0)
        dW1 = self.x.T @ delta_h / batch_size
        db1 = delta_h.mean(axis=0)

        # Update with momentum
        self.dW2_prev = self.lr * dW2 + self.momentum * self.dW2_prev
        self.db2_prev = self.lr * db2 + self.momentum * self.db2_prev
        self.dW1_prev = self.lr * dW1 + self.momentum * self.dW1_prev
        self.db1_prev = self.lr * db1 + self.momentum * self.db1_prev

        self.W2 += self.dW2_prev
        self.b2 += self.db2_prev
        self.W1 += self.dW1_prev
        self.b1 += self.db1_prev

        # Return sum-squared error
        return 0.5 * np.sum(error ** 2) / batch_size

    def predict(self, x):
        return self.forward(x)


# ═══════════════════════════════════════════════════════════════
# DATA GENERATION
# ═══════════════════════════════════════════════════════════════

def make_shift_dataset(n_patterns=256, n_bits=8):
    """
    Generate the training set for the shifter network.

    For each of the 3 shift operations (left, none, right),
    generate random binary patterns and their shifted targets.

    Returns X (n_patterns*3, 11) and Y (n_patterns*3, 8).
    """
    X_list, Y_list = [], []

    for _ in range(n_patterns):
        # Random binary pattern
        pattern = np.random.randint(0, 2, n_bits).astype(float)

        # Shift left (circular): element i gets pattern[(i+1) % n]
        shifted_left = np.roll(pattern, -1)
        x_left = np.concatenate([pattern, [1, 0, 0]])  # shift-left command
        X_list.append(x_left)
        Y_list.append(shifted_left)

        # No shift
        x_none = np.concatenate([pattern, [0, 1, 0]])   # no-shift command
        X_list.append(x_none)
        Y_list.append(pattern.copy())

        # Shift right (circular): element i gets pattern[(i-1) % n]
        shifted_right = np.roll(pattern, 1)
        x_right = np.concatenate([pattern, [0, 0, 1]])   # shift-right command
        X_list.append(x_right)
        Y_list.append(shifted_right)

    X = np.array(X_list)
    Y = np.array(Y_list)
    return X, Y


def make_exhaustive_dataset(n_bits=8):
    """
    Generate ALL 2^n_bits patterns × 3 shifts = 768 training examples.
    This is what the PDP book likely used for small-scale experiments.
    """
    X_list, Y_list = [], []
    for i in range(2 ** n_bits):
        pattern = np.array([(i >> b) & 1 for b in range(n_bits)], dtype=float)

        shifted_left = np.roll(pattern, -1)
        x_left = np.concatenate([pattern, [1, 0, 0]])
        X_list.append(x_left)
        Y_list.append(shifted_left)

        x_none = np.concatenate([pattern, [0, 1, 0]])
        X_list.append(x_none)
        Y_list.append(pattern.copy())

        shifted_right = np.roll(pattern, 1)
        x_right = np.concatenate([pattern, [0, 0, 1]])
        X_list.append(x_right)
        Y_list.append(shifted_right)

    return np.array(X_list), np.array(Y_list)


# ═══════════════════════════════════════════════════════════════
# TRAINING
# ═══════════════════════════════════════════════════════════════

def train(net, X, Y, n_epochs=3000, batch_size=1, verbose=True):
    """
    Train the shifter network.
    Default: online learning (batch_size=1) as in the PDP book.
    """
    n = X.shape[0]

    history = {'epoch': [], 'tss': [], 'accuracy': []}

    for epoch in range(1, n_epochs + 1):
        # Permuted presentation order (as recommended in PDP handbook)
        perm = np.random.permutation(n)
        total_sse = 0

        for start in range(0, n, batch_size):
            idx = perm[start:start + batch_size]
            x_batch = X[idx]
            y_batch = Y[idx]
            net.forward(x_batch)
            sse = net.backward(y_batch)
            total_sse += sse * len(idx)

        # Compute accuracy (output rounded to nearest integer matches target)
        preds = net.predict(X)
        correct = np.all(np.round(preds) == Y, axis=1).mean()

        history['epoch'].append(epoch)
        history['tss'].append(total_sse / n)
        history['accuracy'].append(correct)

        if verbose and (epoch % 100 == 0 or epoch == 1):
            print(f"Epoch {epoch:4d}  |  TSS = {total_sse/n:.4f}  |  "
                  f"Accuracy = {correct*100:.1f}%")

        # Early stopping
        if correct >= 1.0:
            if verbose:
                print(f"\n✓ Solved at epoch {epoch}!")
            break

    return history


# ═══════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════

def plot_training(history, save_path=None):
    """Plot TSS and accuracy over training."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(history['epoch'], history['tss'], color='#e74c3c', linewidth=2)
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Mean Sum-Squared Error', fontsize=12)
    ax1.set_title('Training Error (TSS)', fontsize=14, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)

    ax2.plot(history['epoch'], [a * 100 for a in history['accuracy']],
             color='#2ecc71', linewidth=2)
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Accuracy (%)', fontsize=12)
    ax2.set_title('Classification Accuracy', fontsize=14, fontweight='bold')
    ax2.set_ylim(-5, 105)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('PDP Shifter Network — Training Progress',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def plot_weights(net, save_path=None):
    """Visualize the learned weight matrices."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    im1 = axes[0].imshow(net.W1.T, aspect='auto', cmap='RdBu_r',
                          vmin=-np.abs(net.W1).max(),
                          vmax=np.abs(net.W1).max())
    axes[0].set_xlabel('Input units (0-7: pattern, 8-10: shift command)')
    axes[0].set_ylabel('Hidden units')
    axes[0].set_title('Input → Hidden Weights', fontweight='bold')
    axes[0].set_xticks(range(11))
    axes[0].set_xticklabels([f'i{i}' for i in range(8)] + ['L', 'N', 'R'])
    plt.colorbar(im1, ax=axes[0], shrink=0.8)

    im2 = axes[1].imshow(net.W2, aspect='auto', cmap='RdBu_r',
                          vmin=-np.abs(net.W2).max(),
                          vmax=np.abs(net.W2).max())
    axes[1].set_xlabel('Output units')
    axes[1].set_ylabel('Hidden units')
    axes[1].set_title('Hidden → Output Weights', fontweight='bold')
    axes[1].set_xticks(range(8))
    axes[1].set_xticklabels([f'o{i}' for i in range(8)])
    plt.colorbar(im2, ax=axes[1], shrink=0.8)

    fig.suptitle('PDP Shifter Network — Learned Weights',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def plot_hidden_activations(net, save_path=None):
    """
    Show hidden unit activations for a few example patterns
    under all three shift conditions.
    """
    # Pick 4 interesting patterns
    test_patterns = [
        np.array([1, 0, 0, 0, 0, 0, 0, 0], dtype=float),  # single bit
        np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=float),  # two adjacent
        np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=float),  # alternating
        np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=float),  # half on
    ]
    pattern_names = ['Single bit', 'Two adjacent', 'Alternating', 'Half on']
    shift_names = ['Shift Left', 'No Shift', 'Shift Right']
    shift_codes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    fig, axes = plt.subplots(4, 3, figsize=(14, 12))

    for row, (pattern, pname) in enumerate(zip(test_patterns, pattern_names)):
        for col, (scode, sname) in enumerate(zip(shift_codes, shift_names)):
            x = np.concatenate([pattern, scode]).reshape(1, -1)
            output = net.forward(x)
            hidden = net.h[0]

            ax = axes[row, col]

            # Show: input | hidden | output | target
            if col == 0:
                expected = np.roll(pattern, -1)
            elif col == 1:
                expected = pattern
            else:
                expected = np.roll(pattern, 1)

            # Bar chart of hidden activations
            colors = ['#3498db' if h > 0.5 else '#95a5a6' for h in hidden]
            ax.bar(range(len(hidden)), hidden, color=colors, alpha=0.8)
            ax.set_ylim(0, 1)
            ax.set_title(f'{pname} — {sname}', fontsize=9)

            if col == 0:
                ax.set_ylabel('Hidden activation', fontsize=8)
            if row == 3:
                ax.set_xlabel('Hidden unit', fontsize=8)

            # Annotate: input → output check
            pred = np.round(output[0]).astype(int)
            match = '✓' if np.array_equal(pred, expected.astype(int)) else '✗'
            ax.text(0.98, 0.95, match, transform=ax.transAxes,
                    fontsize=14, fontweight='bold', ha='right', va='top',
                    color='green' if match == '✓' else 'red')

    fig.suptitle('Hidden Unit Activations — Internal Representations',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


def plot_examples(net, n_examples=6, save_path=None):
    """Show input → output examples for all three shifts."""
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(n_examples, 3, figure=fig, hspace=0.5, wspace=0.3)

    shift_names = ['Shift Left', 'No Shift', 'Shift Right']
    shift_codes = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    np.random.seed(123)
    patterns = [np.random.randint(0, 2, 8).astype(float)
                for _ in range(n_examples)]

    for col, (scode, sname) in enumerate(zip(shift_codes, shift_names)):
        for row, pattern in enumerate(patterns):
            ax = fig.add_subplot(gs[row, col])

            x = np.concatenate([pattern, scode]).reshape(1, -1)
            output = net.forward(x)

            if col == 0:
                expected = np.roll(pattern, -1)
            elif col == 1:
                expected = pattern
            else:
                expected = np.roll(pattern, 1)

            # Stacked bar: input (blue) on top, output (green) on bottom
            width = 0.35
            positions = np.arange(8)

            ax.bar(positions - width/2, pattern, width, color='#3498db',
                   alpha=0.8, label='Input')
            ax.bar(positions + width/2, output[0], width, color='#2ecc71',
                   alpha=0.8, label='Output')

            # Target as red dots
            ax.scatter(positions + width/2, expected, color='red',
                       s=30, zorder=5, marker='x', linewidths=2, label='Target')

            ax.set_ylim(-0.1, 1.3)
            ax.set_xticks(positions)
            ax.set_xticklabels([str(int(p)) for p in pattern], fontsize=8)

            if row == 0:
                ax.set_title(sname, fontsize=12, fontweight='bold')
            if col == 0:
                ax.set_ylabel(f'Ex {row+1}', fontsize=9)
            if row == 0 and col == 2:
                ax.legend(fontsize=7, loc='upper right')

    fig.suptitle('PDP Shifter Network — Example Predictions',
                 fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    plt.show()


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("PDP Shifter Network — Rumelhart, Hinton & Williams (1986)")
    print("Chapter 8: Learning Internal Representations")
    print("=" * 60)

    # --- Generate data ---
    print("\n📦 Generating exhaustive training set...")
    X_train, Y_train = make_exhaustive_dataset(n_bits=8)
    print(f"   {X_train.shape[0]} training patterns "
          f"(256 patterns × 3 shifts)")

    # --- Create network ---
    # The PDP book used hidden units for this task
    # Online learning (pattern-by-pattern) with lr=0.1 and momentum=0.9
    net = ShifterNetwork(
        n_input=8, n_shift=3, n_hidden=20, n_output=8,
        lr=0.1, momentum=0.9, weight_range=0.3
    )
    print(f"\n🧠 Network: 11 → {net.n_hidden} → 8")
    print(f"   Learning rate: {net.lr}, Momentum: {net.momentum}")
    total_params = (net.W1.size + net.b1.size + net.W2.size + net.b2.size)
    print(f"   Total parameters: {total_params}")

    # --- Train ---
    print("\n🔄 Training...\n")
    history = train(net, X_train, Y_train, n_epochs=3000, batch_size=1, verbose=True)

    # --- Test ---
    print("\n📊 Testing on all patterns...")
    preds = net.predict(X_train)
    correct = np.all(np.round(preds) == Y_train, axis=1)
    print(f"   Overall accuracy: {correct.mean()*100:.1f}%")

    # Per-shift accuracy
    for i, name in enumerate(['Shift Left', 'No Shift', 'Shift Right']):
        mask = X_train[:, 8+i] == 1
        acc = correct[mask].mean() * 100
        print(f"   {name}: {acc:.1f}%")

    # --- Visualize ---
    save_dir = os.path.dirname(os.path.abspath(__file__))

    print("\n📈 Plotting training curves...")
    plot_training(history, save_path=os.path.join(save_dir, 'pdp_shifter_training.png'))

    print("\n🎨 Plotting weight matrices...")
    plot_weights(net, save_path=os.path.join(save_dir, 'pdp_shifter_weights.png'))

    print("\n🔍 Plotting hidden unit activations...")
    plot_hidden_activations(net, save_path=os.path.join(save_dir, 'pdp_shifter_hidden.png'))

    print("\n📋 Plotting example predictions...")
    plot_examples(net, save_path=os.path.join(save_dir, 'pdp_shifter_examples.png'))

    print("\n✅ Done!")
