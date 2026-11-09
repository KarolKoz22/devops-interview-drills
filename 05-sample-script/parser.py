import re
import sys 
from collections import Counter

RESTART_RE=re.compile(r'container*.(restart|died|OOMKilled)', re.IGNORECASE)
STATUS_CODE_RE=re.compile(r'"\s(5\d{2})\s')

def parse_log(filepath):
    status_counter=Counter()
    restart_count=0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                status_match=STATUS_CODE_RE.search(line)
                if status_match:
                    status_counter[status_match.group(1)]+=1
                restart_match=RESTART_RE.search(line)
                if restart_match:
                    restart_count+=1
        return status_counter, restart_count
    except FileNotFoundError:
        sys.exit(1)

def main():
    if len(sys.argv)!=2:
        print(f"Uzycie: {sys.argv[0]} < plik z logiem")
        sys.exit(1)
    filepath=sys.argv[1]

    status_counter, restart_count = parse_log(filepath)
    print("Podsumowanie:")
    print(f"Restarty kontenerow: {restart_count}")

    print("Statusy HTTP:")
    for status, count in status_counter.items():
        print(f"{status}: {count}")

if __name__=="__main__":
    main()

    