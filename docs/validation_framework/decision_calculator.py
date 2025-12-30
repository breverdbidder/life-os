#!/usr/bin/env python3
"""
Enhanced Validation Framework - Decision Calculator
Automates Phase 4 Go/No-Go decision based on quantitative + qualitative data
"""

def calculate_decision():
    print("="*70)
    print("PHASE 4: GO/NO-GO DECISION CALCULATOR")
    print("="*70)
    print()
    
    # Quantitative Metrics
    print("📊 QUANTITATIVE METRICS (All 4 must be met)")
    print("-" * 70)
    
    visits = int(input("Landing page visits (need 500+): "))
    quant_1 = visits >= 500
    print(f"  {'✅' if quant_1 else '❌'} Visits: {visits} (threshold: 500)")
    
    conversions = int(input("CTA conversions (total clicks on all CTAs): "))
    conversion_rate = (conversions / visits * 100) if visits > 0 else 0
    quant_2 = 3 <= conversion_rate <= 10
    print(f"  {'✅' if quant_2 else '❌'} Conversion Rate: {conversion_rate:.1f}% (threshold: 3-5%)")
    
    interviews = int(input("User interviews completed (need 15+): "))
    quant_3 = interviews >= 15
    print(f"  {'✅' if quant_3 else '❌'} Interviews: {interviews} (threshold: 15)")
    
    would_pay = int(input("Number who said 'would pay' in interviews: "))
    would_pay_pct = (would_pay / interviews * 100) if interviews > 0 else 0
    quant_4 = would_pay_pct >= 30
    print(f"  {'✅' if quant_4 else '❌'} Would Pay: {would_pay_pct:.0f}% (threshold: 30%)")
    
    all_quant_met = quant_1 and quant_2 and quant_3 and quant_4
    print()
    print(f"  Quantitative Score: {sum([quant_1, quant_2, quant_3, quant_4])}/4")
    print()
    
    # Qualitative Signals
    print("🎯 QUALITATIVE STRONG SIGNALS (Need 3+)")
    print("-" * 70)
    
    signals = []
    
    if input("Unprompted feature requests? (y/n): ").lower() == 'y':
        signals.append("Feature requests")
        print("  ✅ Feature requests")
    
    if input("Users asking 'when can I buy?'? (y/n): ").lower() == 'y':
        signals.append("Urgency")
        print("  ✅ Urgency signals")
    
    if input("Referrals to others with problem? (y/n): ").lower() == 'y':
        signals.append("Referrals")
        print("  ✅ Referral activity")
    
    if input("Emotional intensity in interviews? (y/n): ").lower() == 'y':
        signals.append("Emotional")
        print("  ✅ Emotional intensity")
    
    strong_signals_met = len(signals) >= 3
    print()
    print(f"  Strong Signals: {len(signals)}/4 (need 3)")
    print()
    
    # Warning Signals
    print("⚠️ WARNING SIGNALS (Any = YELLOW/RED)")
    print("-" * 70)
    
    warnings = []
    
    if input("Hearing 'nice to have' language? (y/n): ").lower() == 'y':
        warnings.append("Low priority")
        print("  ⚠️ 'Nice to have' language")
    
    if input("No urgency to solve now? (y/n): ").lower() == 'y':
        warnings.append("No urgency")
        print("  ⚠️ No urgency")
    
    if input("Price sensitivity dominates? (y/n): ").lower() == 'y':
        warnings.append("Price sensitive")
        print("  ⚠️ Price sensitivity")
    
    if input("Can't articulate problem clearly? (y/n): ").lower() == 'y':
        warnings.append("Education needed")
        print("  ⚠️ Market education needed")
    
    print()
    print(f"  Warning Signals: {len(warnings)}/4")
    print()
    
    # TAM Check
    print("💰 MARKET SIZE")
    print("-" * 70)
    tam = float(input("Total Addressable Market estimate ($M): "))
    tam_met = tam >= 10
    print(f"  {'✅' if tam_met else '❌'} TAM: ${tam}M (threshold: $10M)")
    print()
    
    # Decision Matrix
    print("="*70)
    print("DECISION MATRIX")
    print("="*70)
    print()
    
    if all_quant_met and strong_signals_met and tam_met and len(warnings) == 0:
        decision = "🟢 GREEN - BUILD MVP"
        print(f"✅ {decision}")
        print()
        print("All conditions met:")
        print(f"  ✅ {visits} visits (>500)")
        print(f"  ✅ {conversion_rate:.1f}% conversion (3-5%)")
        print(f"  ✅ {interviews} interviews (>15)")
        print(f"  ✅ {would_pay_pct:.0f}% would pay (>30%)")
        print(f"  ✅ {len(signals)} strong signals (≥3)")
        print(f"  ✅ ${tam}M TAM (≥$10M)")
        print(f"  ✅ {len(warnings)} warnings (0)")
        print()
        print("🚀 NEXT ACTION: Proceed to Phase 5 (Pre-Build Preparation)")
        
    elif (sum([quant_1, quant_2, quant_3]) >= 2 and len(signals) >= 1) or \
         (all_quant_met and len(warnings) > 0):
        decision = "🟡 YELLOW - PIVOT"
        print(f"⚠️ {decision}")
        print()
        print("Mixed signals detected:")
        print(f"  Quant Score: {sum([quant_1, quant_2, quant_3, quant_4])}/4")
        print(f"  Strong Signals: {len(signals)}/4")
        print(f"  Warnings: {len(warnings)}/4")
        print()
        print("🔄 NEXT ACTION: Reframe positioning and retest (1 week)")
        print()
        print("Consider:")
        if not quant_2:
            print("  - Improve messaging (low conversion)")
        if len(warnings) > 0:
            print(f"  - Address objections: {', '.join(warnings)}")
        if would_pay_pct < 30:
            print("  - Validate pricing/value prop")
        
    else:
        decision = "🔴 RED - KILL IDEA"
        print(f"❌ {decision}")
        print()
        print("Insufficient validation:")
        print(f"  {'❌' if not quant_1 else '✅'} Visits: {visits} (need 500+)")
        print(f"  {'❌' if not quant_2 else '✅'} Conversion: {conversion_rate:.1f}% (need 3-5%)")
        print(f"  {'❌' if not quant_3 else '✅'} Interviews: {interviews} (need 15+)")
        print(f"  {'❌' if not quant_4 else '✅'} Would Pay: {would_pay_pct:.0f}% (need 30%+)")
        print(f"  {'❌' if not strong_signals_met else '✅'} Strong Signals: {len(signals)} (need 3+)")
        print(f"  {'❌' if not tam_met else '✅'} TAM: ${tam}M (need $10M+)")
        print()
        print("🛑 NEXT ACTION: Document lessons learned and move on")
        print()
        print("This doesn't mean your idea was bad - it means this specific")
        print("positioning/market/timing isn't validated. Consider:")
        print("  - Different target customer")
        print("  - Different problem framing")
        print("  - Adjacent market opportunity")
        print("  - Revisit in 6-12 months")
    
    print()
    print("="*70)
    print(f"FINAL DECISION: {decision}")
    print("="*70)
    print()
    
    # Save results
    with open('validation_decision.txt', 'w') as f:
        f.write(f"Validation Decision Report\n")
        f.write(f"={'='*70}\n\n")
        f.write(f"QUANTITATIVE METRICS:\n")
        f.write(f"  Visits: {visits} ({'✅' if quant_1 else '❌'})\n")
        f.write(f"  Conversion: {conversion_rate:.1f}% ({'✅' if quant_2 else '❌'})\n")
        f.write(f"  Interviews: {interviews} ({'✅' if quant_3 else '❌'})\n")
        f.write(f"  Would Pay: {would_pay_pct:.0f}% ({'✅' if quant_4 else '❌'})\n\n")
        f.write(f"QUALITATIVE:\n")
        f.write(f"  Strong Signals: {len(signals)}/4\n")
        f.write(f"  Warnings: {len(warnings)}/4\n\n")
        f.write(f"MARKET:\n")
        f.write(f"  TAM: ${tam}M ({'✅' if tam_met else '❌'})\n\n")
        f.write(f"DECISION: {decision}\n")
    
    print("📄 Report saved to: validation_decision.txt")
    
    return decision


if __name__ == "__main__":
    try:
        result = calculate_decision()
    except KeyboardInterrupt:
        print("\n\n⚠️ Calculator interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
