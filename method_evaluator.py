
from rouge_dataset_results import RougeDatasetResults
from timeout import TimeoutError, timeout
import os
import traceback
import sys

""" Class that runs ROUGE to compare the output of a custom summarization tool
    comparing it to a 'gold standard' reference summary.
    Crated to decouple the single summary calculator.
"""


class MethodEvaluator(object):

    def __init__(self, dataset, text_numbers, method):
        self.dataset = dataset
        self.text_numbers = text_numbers
        self.method = method

    @timeout(10)
    def summarize_text(self, filename):
        # pyrouge needs the model summaries to be stored in a directory without subdirectories.
        if not os.path.exists(MODEL_DIRECTORY):
            os.makedirs(MODEL_DIRECTORY)

        # Makes a summary of the provided file and stores it in the temp folder.
        with open(filename) as fp:
            text = fp.read()

        print "Summarizing " + filename
        summary = self.method(text)

        with open(os.path.join(MODEL_DIRECTORY, MODEL_FILENAME), 'w') as fp:
            fp.write(summary)

    def get_rouge_scores(self):
        results = RougeDatasetResults()

        for i in self.text_numbers:
            print "Evaluating set #" + str(i)

            try:
                result = self.get_rouge_evaluation_for_text(i)

            except TimeoutError:
                print "Timeout summarizing text #%d\n" % i
                results.add_timeout()
                continue

            except Exception as e:
                print "Error summarizing text #%d\n" % i
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)

                results.add_error()
                continue

            print "Text #%d summarized successfully\n" % i
            results.add_success(result)

        return results
