def adc_read(voltage, bits=10, vref=3.3):
    max_val = 2**bits - 1  # 10-bit = 1023
    return int((voltage / vref) * max_val)

def to_moisture(adc_value, dry=850, wet=400):
    if adc_value >= dry: return 0
    if adc_value <= wet: return 100
    return 100 * (dry - adc_value) / (dry - wet)

print(f"{to_moisture(adc_read(1.5)):5.1f}%")