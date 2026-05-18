Feature: Network connectivity validation
  Verify the current machine's public IP, DNS resolution, and route to Google DNS.

  Scenario: 1. Public IP is outside the restricted range
    Given I retrieve my public IP address from "https://ipinfo.io/ip"
    Then my public IP should not fall within the range "101.33.28.0" to "101.33.29.0"

  Scenario: 2. Google public DNS resolves to 8.8.8.8
    When I resolve the domain "google-public-dns-a.google.com"
    Then it should resolve to the IP address "8.8.8.8"

  Scenario: 3. Route to 8.8.8.8 reaches the target within 10 hops
    When I perform a traceroute to "8.8.8.8" with a maximum of 10 hops
    Then the target "8.8.8.8" should be reached within 10 hops
