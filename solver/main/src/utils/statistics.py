def compute_net_profit(tasks, total_gain):
    max_loss = sum( [ t["loss"] for t in tasks ] )

    return total_gain - max_loss
