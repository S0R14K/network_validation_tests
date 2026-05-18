import ipaddress
import platform
import re
import shutil
import socket
import subprocess

import requests
from behave import given, then, when

public_ip_printed = False

def _ip_to_int(ip: str) -> int:
    """Convert a dotted-decimal IPv4 address to an integer."""
    return int(ipaddress.IPv4Address(ip))


def _run_traceroute(target: str, max_hops: int) -> tuple[str, int | None]:
    """
    Run the platform-appropriate traceroute command.

    Returns:
        (raw_output, hop_count_at_which_target_was_reached)
        hop_count is None when the target was not reached.
    """
    if platform.system() == "Windows":
        executable = shutil.which("tracert")
        cmd = [executable, "-h", str(max_hops), "-d", "-w", "3000", target] if executable else None
    else:
        executable = shutil.which("traceroute")
        cmd = [executable, "-I", "-m", str(max_hops), "-n", "-w", "3", target] if executable else None

    if cmd is None:
        raise RuntimeError("No traceroute command found. Expected 'tracert' on Windows or 'traceroute' on Linux.")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
    except FileNotFoundError:
        raise RuntimeError(f"{cmd[0]} command not found on this system.")

    hop_reached = _parse_hop_number(output, target)
    return output, hop_reached


def _parse_hop_number(output: str, target: str) -> int | None:
    """
    Parse traceroute output and return the hop number at which
    *target* first appears, or None if it was never reached.
    """
    for line in output.splitlines():
        m = re.match(r"^\s*(\d+)\s+", line)
        if m and target in line:
            return int(m.group(1))
    return None


@given('I retrieve my public IP address from "{url}"')
def step_retrieve_public_ip(context, url):
    global public_ip_printed

    response = requests.get(url, timeout=10)
    assert response.status_code == 200, (
        f"Failed to retrieve public IP - HTTP {response.status_code}"
    )
    context.public_ip = response.text.strip()

    if not public_ip_printed:
        print(f"\n   Public IP: {context.public_ip}")
        public_ip_printed = True


@then('my public IP should not fall within the range "{start_ip}" to "{end_ip}"')
def step_ip_not_in_range(context, start_ip, end_ip):
    public_ip = context.public_ip

    try:
        ipaddress.IPv4Address(public_ip)
    except ValueError:
        raise AssertionError(
            f"Retrieved value '{public_ip}' is not a valid IPv4 address."
        )

    start_int = _ip_to_int(start_ip)
    end_int   = _ip_to_int(end_ip)

    assert not (start_int <= _ip_to_int(public_ip) <= end_int), (
        f"FAIL: Public IP {public_ip} IS within the restricted range "
        f"{start_ip} - {end_ip}."
    )

    print(f"   {public_ip} is outside the restricted range.")


@when('I resolve the domain "{domain}"')
def step_resolve_domain(context, domain):
    try:
        context.resolved_ip = socket.gethostbyname(domain)
        context.resolved_domain = domain
    except socket.gaierror as exc:
        raise AssertionError(f"DNS resolution failed for '{domain}': {exc}")


@then('it should resolve to the IP address "{expected_ip}"')
def step_assert_resolved_ip(context, expected_ip):
    assert context.resolved_ip == expected_ip, (
        f"FAIL: Expected '{expected_ip}' but got '{context.resolved_ip}'."
    )
    print(f"   {context.resolved_domain} resolved to {expected_ip}.")


@when('I perform a traceroute to "{target}" with a maximum of {max_hops:d} hops')
def step_run_traceroute(context, target, max_hops):
    output, hop_count = _run_traceroute(target, max_hops)

    context.traceroute_output    = output
    context.traceroute_hop_count = hop_count
    context.traceroute_target    = target
    context.traceroute_max_hops  = max_hops

    print(output)


@then('the target "{target}" should be reached within {max_hops:d} hops')
def step_assert_hops(context, target, max_hops):
    hop_count = context.traceroute_hop_count

    assert hop_count is not None, (
        f"FAIL: Target {target} was not reached within {max_hops} hops.\n"
        f"Traceroute output:\n{context.traceroute_output}"
    )

    assert hop_count <= max_hops, (
        f"FAIL: Target {target} was reached at hop {hop_count}, "
        f"which exceeds the maximum allowed {max_hops} hops."
    )

    print(f"  Target reached at hop {hop_count} of {max_hops}.")
