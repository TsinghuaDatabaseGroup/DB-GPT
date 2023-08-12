from abc import ABC, abstractmethod
import numpy as np

class EvaluationResult(ABC):

    @abstractmethod
    def sorted(self, method='default'):
        """Get the results in the form of a sorted prompt and score list.
        Has a method argument to support sorting by various metrics."""
        pass

    @abstractmethod
    def in_place(self, method='default'):
        """Get the results in the form of a list of prompts and scores without sorting."""
        pass

class SQLEvaluationResult:

    def __init__(self, prompts, scores):
        self.prompts = prompts
        self.scores = scores

    def _agg_scores(self, method, i=1):
        """For each prompt, compute a statistic of the scores (e.g., mean, median)"""
        if method == 'mean':
            return [np.mean(s[s[:,0]==1][:,i]) for s in self.scores]
        elif method == 'median':
            return [np.median(s[s[:,0]==1][:,i]) for s in self.scores]
        elif method == 'std':
            return [np.std(s[s[:,0]==1][:,i]) for s in self.scores]
        elif method == 'max':
            return [np.max(s[s[:,0]==1][:,i]) for s in self.scores]
        elif method == 'min':
            return [np.min(s[s[:,0]==1][:,i]) for s in self.scores]
        elif method == 'iqm':
            return [np.mean(np.percentile(lps[lps[:,0]==1][:,i], [25, 75])) for lps in self.scores]
        else:
            raise ValueError('Invalid method: {}'.format(method))
        
    def _agg_accs(self):
        return [np.mean(s[:,0]) for s in self.scores]
    
    def _agg_mean(self, i):
        return [np.mean(s[s[:,0]==1][:,i]) for s in self.scores]

    def sorted_latc(self, method='default'):
        if method == 'default':
            latc = self._agg_scores('mean')
            costs = self._agg_scores('mean', 4)
        else:
            latc = self._agg_scores(method)
            costs = self._agg_scores(method, 4)

        accs = self._agg_accs()
        input_latc = self._agg_mean(2)
        answer_latc = self._agg_mean(3)
        input_costs = self._agg_mean(5)
        answer_costs = self._agg_mean(6)
        results = [[accs[i], -latc[i]/input_latc[i], latc[i], input_latc[i], answer_latc[i], costs[i], input_costs[i], answer_costs[i], self.prompts[i]] for i in range(len(latc))]
        # Sort prompts by score
        sorted_results = sorted(results, reverse=True)
        for i in range(len(results)):
            results[i][1] = - results[i][1]
        return sorted_results
    
    def sorted_costs(self, method='default'):
        if method == 'default':
            costs = self._agg_scores('mean')
        else:
            costs = self._agg_scores(method)

        accs = self._agg_accs()
        input_costs = self._agg_mean(2)
        output_costs = self._agg_mean(3)
        results = [[accs[i], -costs[i]/input_costs[i], costs[i], input_costs[i], output_costs[i], self.prompts[i]] for i in range(len(costs))]
        # Sort prompts by score
        sorted_results = sorted(results, reverse=True)
        for i in range(len(results)):
            results[i][1] = - results[i][1]
        return sorted_results

    def sorted_index_tuning(self, method='default'):
        if method == 'default':
            scores = self._agg_scores('mean')
        else:
            scores = self._agg_scores(method)
        
        #accs = self._agg_accs()
        # 1) the total cost reduction; 2) the success ratio
        results = [[scores[i], self.prompts[i]] for i in range(len(scores))]
        # Sort prompts by score
        sorted_results = sorted(results, reverse=True)
        for i in range(len(results)):
            results[i][0] = - results[i][0]
        return sorted_results

    def in_place(self, method='default'):
        if method == 'default':
            scores = self._agg_scores('mean')
        else:
            scores = self._agg_scores(method)
        return self.prompts, scores