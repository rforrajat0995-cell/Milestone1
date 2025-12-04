"""
Data validation functions for extracted mutual fund data
"""

import re
from typing import Dict, List, Tuple


def validate_expense_ratio(value: str) -> Tuple[bool, str]:
    """
    Validate expense ratio format.
    Expected: percentage value like "0.62%" or "1.25%"
    """
    if not value or not isinstance(value, str):
        return False, "Expense ratio is missing or invalid type"
    
    value = value.strip()
    
    # Check if it's a percentage format
    if value.endswith('%'):
        try:
            num_value = float(value.rstrip('%'))
            if 0 <= num_value <= 10:  # Reasonable range for expense ratio
                return True, ""
            else:
                return False, f"Expense ratio {num_value}% is outside reasonable range (0-10%)"
        except ValueError:
            return False, f"Expense ratio '{value}' is not a valid number"
    else:
        return False, f"Expense ratio '{value}' does not end with %"


def validate_exit_load(value: str) -> Tuple[bool, str]:
    """
    Validate exit load format.
    Expected: "Nil" or percentage like "1%" or "1.5%" or conditional like "Exit load of 0.25%, if redeemed within 30 days"
    """
    if not value or not isinstance(value, str):
        return False, "Exit load is missing or invalid type"
    
    value = value.strip()
    
    # Accept "Nil" or "NIL" or "NA" or "N/A"
    if value.upper() in ["NIL", "NA", "N/A", "NONE", ""]:
        return True, ""
    
    # Check if it contains a conditional description (like "Exit load of 0.25%, if redeemed within 30 days")
    if "exit load" in value.lower() and "%" in value:
        # Extract percentage from the description
        import re
        percentage_match = re.search(r'([0-9.]+)%', value)
        if percentage_match:
            try:
                num_value = float(percentage_match.group(1))
                if 0 <= num_value <= 10:  # Reasonable range
                    return True, ""  # Accept conditional exit load descriptions
            except ValueError:
                pass
    
    # Check if it's a simple percentage format
    if value.endswith('%'):
        try:
            num_value = float(value.rstrip('%'))
            if 0 <= num_value <= 10:  # Reasonable range
                return True, ""
            else:
                return False, f"Exit load {num_value}% is outside reasonable range (0-10%)"
        except ValueError:
            return False, f"Exit load '{value}' is not a valid number"
    else:
        # Accept conditional descriptions that contain percentage
        if "%" in value and any(char.isdigit() for char in value):
            return True, ""  # Accept descriptive exit load formats
    
    return False, f"Exit load '{value}' is not in expected format (Nil, percentage, or conditional description)"


def validate_minimum_sip(value: str) -> Tuple[bool, str]:
    """
    Validate minimum SIP amount.
    Expected: Amount with ₹ symbol like "₹1000" or "₹500"
    """
    if not value or not isinstance(value, str):
        return False, "Minimum SIP is missing or invalid type"
    
    value = value.strip()
    
    # Remove ₹ symbol and commas, extract number
    cleaned = value.replace('₹', '').replace(',', '').replace(' ', '')
    
    try:
        num_value = float(cleaned)
        if num_value >= 0 and num_value <= 1000000:  # Reasonable range
            return True, ""
        else:
            return False, f"Minimum SIP {num_value} is outside reasonable range"
    except ValueError:
        return False, f"Minimum SIP '{value}' does not contain a valid number"


def validate_lock_in(value: str) -> Tuple[bool, str]:
    """
    Validate lock-in period.
    Expected: "N/A", "NA", "3Y", "3 Years", "3Yr", etc. or empty for non-ELSS funds
    """
    if not value or not isinstance(value, str):
        return False, "Lock-in is missing or invalid type"
    
    value = value.strip().upper()
    
    # Accept "N/A", "NA", "NONE", empty string for non-ELSS funds
    if value in ["N/A", "NA", "NONE", ""]:
        return True, ""
    
    # Check for year format: 3Y, 3YRS, 3 YEARS, etc.
    year_pattern = re.compile(r'(\d+)\s*(Y|YR|YRS|YEAR|YEARS)', re.IGNORECASE)
    match = year_pattern.search(value)
    if match:
        years = int(match.group(1))
        if 0 <= years <= 20:  # Reasonable range
            return True, ""
        else:
            return False, f"Lock-in period {years} years is outside reasonable range"
    
    return False, f"Lock-in '{value}' is not in expected format (N/A or X years)"


def validate_riskometer(value: str) -> Tuple[bool, str]:
    """
    Validate riskometer value.
    Expected: Risk level description like "Moderately High Risk", "Low Risk", etc.
    """
    if not value or not isinstance(value, str):
        return False, "Riskometer is missing or invalid type"
    
    value = value.strip()
    
    if len(value) < 3:
        return False, "Riskometer value is too short"
    
    # Common risk levels (not exhaustive, but helpful for validation)
    risk_keywords = ["LOW", "MODERATE", "HIGH", "VERY", "RISK"]
    value_upper = value.upper()
    
    if any(keyword in value_upper for keyword in risk_keywords):
        return True, ""
    else:
        # Still accept if it's a reasonable string (might be a valid description we don't know)
        if len(value) > 5:
            return True, ""  # Accept as valid if it's a reasonable length
        return False, "Riskometer value does not appear to be a valid risk description"


def validate_benchmark(value: str) -> Tuple[bool, str]:
    """
    Validate benchmark value.
    Expected: Index name like "Nifty 500 Total Return Index"
    """
    if not value or not isinstance(value, str):
        return False, "Benchmark is missing or invalid type"
    
    value = value.strip()
    
    if len(value) < 3:
        return False, "Benchmark value is too short"
    
    # Should contain index-related keywords
    index_keywords = ["INDEX", "NIFTY", "SENSEX", "BSE", "NSE"]
    value_upper = value.upper()
    
    if any(keyword in value_upper for keyword in index_keywords):
        return True, ""
    else:
        # Still accept if it's a reasonable string (might be a valid benchmark we don't know)
        if len(value) > 5:
            return True, ""
        return False, "Benchmark value does not appear to be a valid index name"


def validate_returns(value: str, period: str = "") -> Tuple[bool, str]:
    """
    Validate returns format.
    Expected: percentage value like "12.5%" or "-5.2%" (can be negative)
    Returns are optional, so None/empty is acceptable.
    """
    # Returns are optional - if None or empty, that's fine
    if not value or value is None:
        return True, ""
    
    if not isinstance(value, str):
        return False, f"{period} returns is invalid type (expected string)"
    
    value = value.strip()
    
    # Accept "N/A" or "NA" if returns not available
    if value.upper() in ["N/A", "NA", "NONE", ""]:
        return True, ""
    
    # Check if it's a percentage format (can be negative)
    if value.endswith('%'):
        try:
            num_value = float(value.rstrip('%'))
            # Returns can be negative (losses) or very high (gains)
            # Reasonable range: -100% (total loss) to 1000% (10x return)
            if -100 <= num_value <= 1000:
                return True, ""
            else:
                return False, f"{period} returns {num_value}% is outside reasonable range (-100% to 1000%)"
        except ValueError:
            return False, f"{period} returns '{value}' is not a valid number"
    else:
        # Try to parse as number and add %
        try:
            num_value = float(value)
            if -100 <= num_value <= 1000:
                return True, ""
            else:
                return False, f"{period} returns {num_value}% is outside reasonable range"
        except ValueError:
            return False, f"{period} returns '{value}' is not in expected format (percentage)"


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate URL format and structure.
    """
    if not url or not isinstance(url, str):
        return False, "URL is missing or invalid type"
    
    url = url.strip()
    
    # Basic URL validation
    if not url.startswith("http://") and not url.startswith("https://"):
        return False, "URL must start with http:// or https://"
    
    if "groww.in/mutual-funds/" not in url:
        return False, "URL must be a Groww mutual fund page"
    
    if len(url) < 20:
        return False, "URL is too short to be valid"
    
    return True, ""


def validate_all_fields(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate all fields in the extracted data.
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate URL first
    if "source_url" in data:
        is_valid, error = validate_url(data["source_url"])
        if not is_valid:
            errors.append(f"URL validation: {error}")
    else:
        errors.append("Missing source_url field")
    
    # Validate each field
    field_validators = {
        "expense_ratio": validate_expense_ratio,
        "exit_load": validate_exit_load,
        "minimum_sip": validate_minimum_sip,
        "lock_in": validate_lock_in,
        "riskometer": validate_riskometer,
        "benchmark": validate_benchmark,
        # Returns are optional - only validate if present
        "returns_1y": lambda v: validate_returns(v, "1Y"),
        "returns_3y": lambda v: validate_returns(v, "3Y"),
        "returns_5y": lambda v: validate_returns(v, "5Y"),
        "returns_since_inception": lambda v: validate_returns(v, "Since Inception"),
    }
    
    for field, validator in field_validators.items():
        if field in data:
            is_valid, error = validator(data[field])
            if not is_valid:
                errors.append(f"{field}: {error}")
        else:
            # Only require core fields, returns are optional
            if field not in ["returns_1y", "returns_3y", "returns_5y", "returns_since_inception"]:
                errors.append(f"Missing field: {field}")
    
    return len(errors) == 0, errors

