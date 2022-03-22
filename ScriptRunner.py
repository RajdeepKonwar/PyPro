from subprocess import Popen, PIPE

class Runner:
    def __init__(self, path):
        self.path = path

    def Run(self):
        print('Profiling...')
        p = Popen(['python', self.path], stdout=PIPE, stderr=PIPE)
        output, errors = p.communicate()
        print(output.decode('utf-8'))
        print(errors.decode('utf-8'))
        p.wait()
        print('Profiling complete!\n')
