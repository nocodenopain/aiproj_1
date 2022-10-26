import dns.resolver
import dns.rdatatype
from colorama import Fore
from colorama import Style

root_servers = ["198.41.0.4",  # a.root-servers.net
                "199.9.14.201",  # b.root-servers.net
                "192.33.4.12",  # c.root-servers.net
                "199.7.91.13",  # d.root-servers.net
                "192.203.230.10",  # e.root-servers.net
                "192.5.5.241",  # f.root-servers.net
                "192.112.36.4",  # g.root-servers.net
                "198.97.190.53",  # h.root-servers.net
                "192.36.148.17",  # i.root-servers.net
                "192.58.128.30",  # j.root-servers.net
                "193.0.14.129",  # k.root-servers.net
                "199.7.83.42",  # l.root-servers.net
                "202.12.27.33"]  # m.root-servers.net


def resolve_host(hostname: str, rrtype: dns.rdatatype, rd: int):
    if rd == 1:
        __resolve_rec(hostname, rrtype)
    elif rd == 0:
        __resolve_no_rec(hostname, rrtype)
    else:
        print("[Debug] Invalid rd: " + str(rd))


def __resolve_rec(hostname: str, rrtype: dns.rdatatype):
    print("[Debug] Resolving host with RD=1: \"" + hostname + "\"")

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["8.8.8.8"]  # Default Server
    answers = resolver.resolve(qname=hostname, rdtype=rrtype, raise_on_no_answer=False)

    __show_result(answers=answers, target=hostname, rrtype=rrtype, resolver=resolver)


def __resolve_no_rec(hostname: str, rrtype: dns.rdatatype):
    print("[Debug] Resolving host with RD=0: \"" + hostname + "\"")

    show_process = __show_prompt("Show process?")
    (answers, resolver) = __resolve_iter(hostname=hostname, rrtype=rrtype, show_process=show_process)

    __show_result(answers=answers, target=hostname, rrtype=rrtype, resolver=resolver)


def __resolve_iter(hostname: str, rrtype: dns.rdatatype, show_process: bool = False):
    resolver = dns.resolver.Resolver(configure=False)
    resolver.flags = 0
    resolver.timeout = 3

    tokens = hostname.split(".")

    if len(tokens) == 1:
        __resolve_ns_iter(resolver=resolver, hostname=hostname, show_process=show_process)

    target = None
    for i in reversed(tokens[1:]):
        target = (i + "." + target) if target is not None else i
        __resolve_ns_iter(resolver=resolver, hostname=target, show_process=show_process)

    answers = resolver.resolve(hostname, rdtype=rrtype, raise_on_no_answer=False)
    return answers, resolver


def __resolve_ns_iter(resolver: dns.resolver.Resolver, hostname: str, show_process: bool = False):
    if show_process:
        print("[Iterator] Iterating NS Query to NameServer: \"" + hostname + "\"")

    if not resolver.nameservers:
        resolver.nameservers = root_servers
    answers = resolver.resolve(qname=hostname, rdtype=dns.rdatatype.NS, raise_on_no_answer=False)
    hostnames = []

    ext_nameservers = []

    __rr_append(nameservers=ext_nameservers, hostnames=hostnames, rdset=answers.response.answer, show_process=show_process)
    if show_process:
        print("[Iterator] Completed answer info processing.\n")

    __rr_append(nameservers=ext_nameservers, hostnames=hostnames, rdset=answers.response.authority, show_process=show_process)
    if show_process:
        print("[Iterator] Completed authority info processing.\n")

    __rr_append(nameservers=ext_nameservers, hostnames=hostnames, rdset=answers.response.additional, show_process=show_process)
    if show_process:
        print("[Iterator] Completed additional info processing.\n")

    for i in hostnames:
        __fetch_ns_ip(target=i, resolver=resolver, nameservers=ext_nameservers, show_process=show_process)

    resolver.nameservers = list(dict.fromkeys(ext_nameservers))
    if show_process:
        print(resolver.nameservers)
        print("[Iterator] Duplicates removed. Completed nameserver resolving.\n")


def __rr_append(nameservers: list, hostnames: list, rdset: dns.rdataset, show_process: bool = False):
    for i in rdset:
        if i.rdtype == dns.rdatatype.A:
            for j in i:
                if show_process:
                    print("[Iterator] Adding RR: " + j.to_text())
                nameservers.append(j.to_text())
        elif i.rdtype != dns.rdatatype.AAAA:
            for j in i:
                if show_process:
                    print("[Iterator] Adding hostname: " + j.to_text().rstrip("."))
                hostnames.append(j.to_text().rstrip("."))
        else:
            if show_process:
                print("[Iterator] Skipping type: " + dns.rdatatype.to_text(i.rdtype))


def __get_rr_recur_branch__(result: list, answers: dns.resolver.Answer, records: dns.rdataset, target: str,
                            rrtype: dns.rdatatype):
    for i in records:
        if str(i.name).rstrip(".") == target:
            if i.rdtype == rrtype:
                for j in i:
                    result.append(j)
            else:
                for j in i:
                    result0 = __get_rr_recur(answers=answers, target=str(j).rstrip("."), rrtype=rrtype)
                    if result0:
                        result.extend(result0)
                    else:
                        (answers0, resolver0) = __resolve_iter(hostname=str(j).rstrip("."), rrtype=dns.rdatatype.A)
                        for k in answers0.response.answer:
                            if k.rdtype == rrtype:
                                for x in k:
                                    result.append(x)


def __get_rr_recur(answers: dns.resolver.Answer, target: str, rrtype: dns.rdatatype,
                   resolver: dns.resolver.Resolver = None):
    result = []
    __get_rr_recur_branch__(result=result, answers=answers, records=answers.response.answer, target=target, rrtype=rrtype)
    __get_rr_recur_branch__(result=result, answers=answers, records=answers.response.authority, target=target,
                            rrtype=rrtype)
    __get_rr_recur_branch__(result=result, answers=answers, records=answers.response.additional, target=target,
                            rrtype=rrtype)
    return result


def __ns_append(nameservers: list, target: dns.rdataset, answers: dns.resolver.Answer, show_process: bool = False):
    for j in target:
        if j.rdtype == dns.rdatatype.A:
            for k in j:
                if show_process:
                    print("[Iterator] Nameserver adding record: " + k.to_text())
                nameservers.append(k.to_text())
        else:
            for k in j:
                result0 = __get_rr_recur(answers=answers, target=k, rrtype=dns.rdatatype.from_text("A"))
                nameservers.extend(result0)


def __fetch_ns_ip(target: str, resolver: dns.resolver.Resolver = None,
                  nameservers: list = root_servers, show_process: bool = False):
    try:
        if resolver is None:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.flags = 0
            resolver.nameservers = nameservers
        answers0 = resolver.resolve(qname=target, rdtype=dns.rdatatype.A, raise_on_no_answer=False)
        __ns_append(nameservers=nameservers, target=answers0.response.answer,
                    answers=answers0, show_process=show_process)
        __ns_append(nameservers=nameservers, target=answers0.response.authority,
                    answers=answers0, show_process=show_process)
        __ns_append(nameservers=nameservers, target=answers0.response.additional,
                    answers=answers0, show_process=show_process)
    except (dns.resolver.NoNameservers, dns.resolver.NoAnswer):
        if show_process:
            print(f"{Fore.RED}[Fetch RR] RR \"" + target + f"\" is not resolved. {Style.RESET_ALL}Skipped.")


def __show_prompt(text: str):
    prompt = input("==> " + text + " [Y/N]: ")

    while prompt.lower() != "y" and prompt.lower() != "n":
        prompt = input("==> Unrecognized option: \"" + prompt + "\". " + text + " [Y/N]: ")
    if prompt.lower() == 'y':
        return True
    return False


def __show_result(answers: dns.resolver.Answer, target: str, rrtype: dns.rdatatype, resolver: dns.resolver.Resolver):
    print("\n[Show Result] Ready.")

    print("\n===Result===")
    print(str(__get_rr_recur(answers=answers, target=target, rrtype=rrtype, resolver=resolver)))

    print("\n===Info===")
    print("Authoritative Answer: " + str(answers.response.flags & 0x0400 == 0x0400))  # The flag bit is at bit[10]
    print("Flags detected: " + str(answers.response.flags))

    if __show_prompt("Show possible nameservers that returned this query response?"):
        print("\n===Nameservers===")
        for i in reversed(resolver.nameservers):
            print("\t\t" + str(i))

    if __show_prompt("Show original response?"):
        print("\n===Original Response===")
        print(str(answers.response))

    if __show_prompt("Show recursive result?"):
        print("Sorry, can't show because I don't want to implement this.")


def main():
    hostname = input("Input Hostname: ")
    rrtype = input("Type: ")
    rd = input("RD (0 or 1 for \"No recursion\" or \"Recursion Desired\"): ")
    resolve_host(hostname, dns.rdatatype.from_text(rrtype), int(rd))


def test():
    resolve_host("www.sustech.edu.cn", dns.rdatatype.from_text("A"), 0)


if __name__ == "__main__":
    try:
        main()
        # test()

    except KeyboardInterrupt:
        pass
