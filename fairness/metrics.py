
import numpy as np, pandas as pd

def demographic_parity(scores, groups, threshold=0.5):
    # scores: list of float scores (0-1)
    # groups: list of protected group labels corresponding to scores
    df = pd.DataFrame({'score': scores, 'group': groups})
    df['selected'] = df['score'] >= threshold
    rates = df.groupby('group')['selected'].mean().to_dict()
    return rates

def equalized_odds(y_true, y_pred, groups):
    # y_true: binary labels (hire decisions), y_pred: binary predictions, groups: protected labels
    df = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred, 'group': groups})
    metrics = {}
    for g, sub in df.groupby('group'):
        tp = ((sub.y_true==1) & (sub.y_pred==1)).sum()
        fn = ((sub.y_true==1) & (sub.y_pred==0)).sum()
        fp = ((sub.y_true==0) & (sub.y_pred==1)).sum()
        tn = ((sub.y_true==0) & (sub.y_pred==0)).sum()
        tpr = tp / (tp+fn) if (tp+fn)>0 else None
        fpr = fp / (fp+tn) if (fp+tn)>0 else None
        metrics[g] = {'tpr': tpr, 'fpr': fpr}
    return metrics
