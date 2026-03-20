from thefuzz import fuzz

# Sample identifiers with variations
identifiers = [
    "CUST-001234",
    "CUSTOMER-001234",
    "cust_001234",
    "PROD-ABC123",
    "PRODUCT-ABC123",
    "Product ABC-123",
    "EMP-789456",
    "EMPLOYEE-789456",
    "emp_789456",
]

# Find fuzzy matches
print("Fuzzy Matches (score >= 80):")
for i, id1 in enumerate(identifiers):
    for id2 in identifiers[i + 1 :]:
        score = fuzz.token_set_ratio(id1, id2)
        if score >= 80:
            print(f"{id1:15} ↔ {id2:15} ({score})")

# Quick comparison
print("\nQuick comparisons:")
test_pairs = [("CUST-001234", "CUSTOMER-001234"), ("PROD-ABC123", "Product ABC-123")]
for a, b in test_pairs:
    print(f"{a} vs {b}: {fuzz.token_set_ratio(a, b)}")
