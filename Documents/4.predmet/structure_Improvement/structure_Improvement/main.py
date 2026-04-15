from Generate_year9 import generate_year9_students
from Generate_year1 import generate_year1_students
# from Generate_year2 import generate_year2_students

# ==============================================================================
# MAIN SCRIPT - Generate students across multiple years
# ==============================================================================

def main():
    print("="*70)
    print("GENERATING STUDENT DATA")
    print("="*70)
    
    # ======================================================================
    # Step 1: Generate Year 9 students
    # ======================================================================
    print("\n[1/2] Generating Year 9 students...")
    year9_students = generate_year9_students(id_student=0, num_student=100)
    print(f"✓ Generated {len(year9_students)} Year 9 students")
    
    # Show sample Year 9 student
    sample_y9 = year9_students[0]
    print(f"\nSample Year 9 student:")
    print(f"  ID: {sample_y9['id']}")
    print(f"  Grade9: {sample_y9['grade9']}")
    print(f"  Mat9: {sample_y9['mat9']}, Slo9: {sample_y9['slo9']}, Ang9: {sample_y9['ang9']}")
    
    # ======================================================================
    # Step 2: Generate Year 1 students (based on Year 9 data)
    # ======================================================================
    print("\n[2/2] Generating Year 1 students based on Year 9 data...")
    year1_students = generate_year1_students(year9_data=year9_students)
    print(f"✓ Generated {len(year1_students)} Year 1 students")
    
    # Show sample Year 1 student
    sample_y1 = year1_students[0]
    print(f"\nSample Year 1 student (same ID as above):")
    print(f"  ID: {sample_y1['id']}")
    print(f"  Grade1: {sample_y1['grade1']}")
    print(f"  Mat1: {sample_y1['mat1']}, Slo1: {sample_y1['slo1']}, Ang1: {sample_y1['ang1']}")
    print(f"  [Year 9 reference: Mat9: {sample_y1['mat9']}, Slo9: {sample_y1['slo9']}, Ang9: {sample_y1['ang9']}]")
    
    # ======================================================================
    # Show progression statistics
    # ======================================================================
    print("\n" + "="*70)
    print("PROGRESSION ANALYSIS (Year 9 → Year 1)")
    print("="*70)
    
    improved = 0
    declined = 0
    stayed_same = 0
    
    for y1 in year1_students:
        mat_change = y1['mat1'] - y1['mat9']
        if mat_change > 0:
            improved += 1
        elif mat_change < 0:
            declined += 1
        else:
            stayed_same += 1
    
    print(f"\nMathematics progression:")
    print(f"  Improved: {improved} students ({improved/len(year1_students)*100:.1f}%)")
    print(f"  Declined: {declined} students ({declined/len(year1_students)*100:.1f}%)")
    print(f"  Stayed same: {stayed_same} students ({stayed_same/len(year1_students)*100:.1f}%)")
    
    # Show some examples of big changes
    print("\nExamples of students who changed significantly:")
    for y1 in year1_students[:20]:
        mat_change = y1['mat1'] - y1['mat9']
        if abs(mat_change) >= 2:
            direction = "↑" if mat_change > 0 else "↓"
            print(f"  ID {y1['id']}: Mat9={y1['mat9']} → Mat1={y1['mat1']} ({direction} {abs(mat_change)} grades!)")
    
    print("\n" + "="*70)
    print("✓ Data generation complete!")
    print("="*70)
    
    return year9_students, year1_students


if __name__ == "__main__":
    year9_data, year1_data = main()
