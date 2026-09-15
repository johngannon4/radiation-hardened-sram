import matplotlib.pyplot as plt


def plot_single(ax, df, label):
    # basic helper to plot one waveform on a given axis
    ax.plot(df["time"], df["value"], label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.3)


def plot_transient_signals(d, d2, q1b, current):
    # visualize input/output behavior together with supply current
    # top: logic-level signals (D, D2, Q1B)
    # bottom: current drawn from VDD
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))

    plot_single(axes[0], d, "D")
    plot_single(axes[0], d2, "D2")
    plot_single(axes[0], q1b, "Q1B")
    axes[0].set_title("Transient Waveforms")
    axes[0].legend()

    plot_single(axes[1], current, "I(VDD)")
    axes[1].set_title("Supply Current")
    axes[1].legend()

    plt.tight_layout()
    return fig


def plot_seu_cases(seu_dict):
    # compare node response under different SEU injection scenarios
    # each curve corresponds to a different disturbance condition
    fig, ax = plt.subplots(figsize=(10, 5))

    for name, df in seu_dict.items():
        ax.plot(df["time"], df["value"], label=name)

    ax.set_title("SEU Response under Different Injection Conditions")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Node Voltage (V)")
    ax.grid(alpha=0.3)
    ax.legend()

    plt.tight_layout()
    return fig


def plot_snm_curve(snm_df):
    # plot the SNM-related curve (used here as a qualitative stability indicator)
    # note: this is not a full butterfly curve, just the available data representation
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(snm_df["time"], snm_df["value"])
    ax.set_title("SNM-Derived Curve")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    return fig