import sys


class KLMCalculator():
    def calcKLM(self, dictionary):
        time = 0.0
        if (len(sys.argv) == 2):
            file = open(sys.argv[1])
            for line in file:
                line = line.replace("\n", "")
                line = line.replace(" ", "")
                line = line.partition('#')[0]
                line = line.rstrip()
                time += self.calcKLMForLine(line, dictionary)
        return time

    def calcKLMForLine(self, line, dictionary):
        lineKLM = 0.0
        number = ""
        for c in line:
            c = c.lower()
            if c.isdigit():
                number += c
            else:
                if number != "":
                    lineKLM += int(number) * dictionary[c]
                    number = ""
                else:
                    lineKLM += dictionary[c]
        return lineKLM


def main():
    klmDict = {"k": 0.28, "p": 1.1, "b": 0.1, "h": 0.4, "m": 1.2, "w": 0.0}
    expDict = {"k": 0.14, "p": 0.5, "b": 0.11, "h": 0.54, "m": 1.2, "w": 0.0}

    klm = KLMCalculator()
    print("Original KLM operators (prediction time in seconds): " + str(klm.calcKLM(klmDict)))
    print("Own measured KLM operators (prediction time in seconds): " + str(klm.calcKLM(expDict)))


if __name__ == '__main__':
    main()
