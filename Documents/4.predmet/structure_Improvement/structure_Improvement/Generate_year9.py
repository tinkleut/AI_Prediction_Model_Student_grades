import random 

# STUDENT DATA GENERATOR FOR GRADE 9
# This function generates student data for 9th grade students.
# It creates realistic grade distributions across three subjects:
# - grade9: Overall grade (average of the three subjects)
# - mat9: Mathematics grade
# - slo9: Slovenian language grade  
# - ang9: English language grade
#
# The generator models realistic patterns:
# - Weighted distribution (9th graders are motivated before high school)
# - U-shaped variance (extremes are consistent, middle grades vary more)
# - Subject difficulty (English easier than Slovenian, Math hardest)
# - Language correlation (Slovenian and English grades stay close)
# - Asymmetric noise (boundary-aware - can't go above 5 or below 2)

def generate_year9_students(id_student, num_student):

    random.seed(1)  # Set seed for reproducibility

    """
    Generate grade 9 student data.
    
    id_student: Starting student ID number
    num_student: Number of students to generate
        
    Returns:
        List of dictionaries, each containing:
        - id: student ID
        - grade9: overall grade (2-5)
        - mat9: mathematics grade (2-5)
        - slo9: Slovenian grade (2-5)
        - ang9: English grade (2-5)
    """
    # Cohort-level effects: random factors affecting all students
    # These represent: teaching quality, curriculum difficulty, exam standards
    # Range: -0.3 to +0.3 per subject (reduced alongside language noise)
    cohort_slo_effect = random.uniform(-0.4, 0.2)
    cohort_ang_effect = random.uniform(-0.4, 0.2)
    
    
    data = []  # List to store all generated students
    
    # Generate each student one by one
    for _ in range(num_student):
        id_student = id_student + 1

        # Add random variation for subject grade balances
        # This will randomly shift a few percent between adjacent grades
        english_34_shift = random.choice([-0.05, 0.05])  # English: grade 3 vs 4
        slovenian_34_shift = random.choice([-0.05, 0.05])  # Slovenian: grade 3 vs 4  
        math_23_shift = random.choice([-0.1, 0.1])  # Math: grade 2 vs 3 (with bias toward 3)

        # STEP 1: Generate overall grade9 with weighted distribution
        # Pattern: 4 > 3 > 5 > 2 (most 4s, then 3s, then 5s, least 2s)
        # Reasoning: 9th graders are motivated but realistic distribution
        # 4% of Year 9 students are excluded (had grade 1 in a subject, couldn't enter high school)
        # Remaining 96% distribution: ~8% grade 2, ~38% grade 3, ~32% grade 4, ~18% grade 5
        # Adjusted to create more balanced spread for subject-specific distributions
        grade9 = random.choices([2, 3, 4, 5], weights=[22, 35, 25, 18])[0]
        # ======================================================================
        # U-shaped variance means:
        # - Students with grade 5: very consistent (mostly get 4s and 5s in subjects)
        # - Students with grade 4: somewhat consistent (mostly 3s, 4s, 5s)
        # - Students with grade 3: LEAST consistent (can get 2, 3, 4, or 5)
        # - Students with grade 2: very consistent (mostly get 2s and 3s in subjects)
        #
        # This reflects reality: struggling and excelling students are predictable,
        # middle students are more variable
        # Increased variance for math to create more spread
        if grade9 == 5:
            noise_std = 0.8  # Increased variance for more spread
        elif grade9 == 4:
            noise_std = 1.1  # Increased variance
        elif grade9 == 3:
            noise_std = 1.4  # Increased variance for more unpredictability
        else:  # grade9 == 2
            noise_std = 0.8  # Increased variance

        # ======================================================================
        # STEP 3: Generate Mathematics grade (mat9)
        # ======================================================================
        # Math is the HARDEST subject, so it has downward bias for good students
        # Increased downward bias to create right-skewed distribution with more 2s
        
        # Start with Gaussian (normal) noise centered at 0
        base_noise = random.gauss(0, noise_std)
        
        # Apply asymmetric bias based on grade level:
        if grade9 == 5:
            # Grade 5 students: strong downward bias (math is hard, rare 5s)
            biased_noise = base_noise - 0.55
        elif grade9 == 4:
            # Grade 4 students: moderate downward bias (math is challenging) - increased for more 3s
            biased_noise = base_noise - 0.65
        elif grade9 == 3:
            # Grade 3 students: slight downward bias (middle ground) with opposite random variation
            biased_noise = base_noise - 0.1 - math_23_shift
        elif grade9 == 2:
            # Grade 2 students: upward bias (can't go below 2, room to improve) with random variation
            biased_noise = base_noise + 0.1 + math_23_shift


        # Calculate mat9 by adding biased noise to grade9, then round to integer
        mat9 = round(grade9 + biased_noise)
        
        # Clamp to valid range [2, 5] (grades 1 don't exist in this system)
        mat9 = max(2, min(5, mat9))

        # ======================================================================
        # STEP 4: Generate Language grades (slo9 and ang9) with weak correlation
        # ======================================================================
        # Languages have some correlation but allow for significant variation
        # Some students are better at native language, others at English
        
        # Create a shared language base
        # Adjusted for desired distributions - higher base for English
        lang_base = grade9 + random.gauss(0, 0.4)

        # Generate individual noise for each language
        slo_noise = random.gauss(0, 0.25)  # Reduced for more consistency
        ang_noise = random.gauss(0, 0.25)  # Reduced for more consistency
        
        # Apply subject-specific base adjustments for Slovenian
        if grade9 == 4:
            slo_base_adjust = -0.2  # Reduce Slovenian base for grade 4 students
        elif grade9 == 3:
            slo_base_adjust = 0.3   # Increase Slovenian base for grade 3 students
        else:
            slo_base_adjust = 0
        
        # Add random variation for subject grade balances
        # This will randomly shift a few percent between adjacent grades
        english_34_shift = random.choice([-0.1, 0.1])  # English: grade 3 vs 4
        slovenian_34_shift = random.choice([-0.1, 0.1])  # Slovenian: grade 3 vs 4  
        math_23_shift = random.choice([-0.1, 0.1])  # Math: grade 2 vs 3 (with bias toward 3)
        
        # Apply asymmetric bias based on grade level:
        # Adjusted for desired distributions
        if grade9 == 5:
            slo_noise -= 0.3  # Slovenian: stronger downward bias to reduce 5s
            ang_noise -= 0.35  # English: maximum downward bias to reduce 5s
        elif grade9 == 4:
            slo_noise -= 0.1 + slovenian_34_shift  # Slovenian: additional downward bias with random variation
            ang_noise -= 0.05 + english_34_shift  # English: slight upward bias with random variation
        elif grade9 == 3:
            slo_noise += 0.2 - slovenian_34_shift  # Slovenian: additional upward bias with opposite random variation
            ang_noise += 0.2 - english_34_shift  # English: upward bias with opposite random variation
        elif grade9 == 2:
            slo_noise += 0.1  # Slovenian: upward bias
            ang_noise += 0.1   # English: upward bias

        # Calculate language grades by adding noise to lang_base, then round
        # Also add cohort-level effects that affect all students
        slo9 = round((lang_base + slo_base_adjust) + slo_noise + cohort_slo_effect)
        ang9 = round(lang_base + ang_noise + cohort_ang_effect)  # No extra boost for English to allow more 2s

        # Clamp both languages to valid range [2, 5]
        slo9 = max(2, min(5, slo9))
        ang9 = max(2, min(5, ang9))

        # ======================================================================
        # STEP 5: Weak language correlation constraint (optional adjustment)
        # ======================================================================
        # Allow languages to differ by up to 2 points for more realism
        # Only adjust if difference is extreme (>2 points)
        if abs(slo9 - ang9) > 2:
            # Adjust towards each other but don't force them to be within 1
            if slo9 > ang9:
                slo9 -= 1  # Reduce difference
                ang9 += 1
            else:
                ang9 -= 1  # Reduce difference
                slo9 += 1
            # Re-clamp after adjustment
            slo9 = max(2, min(5, slo9))
            ang9 = max(2, min(5, ang9))

        # ======================================================================
        # STEP 6: Apply averaging constraint
        # ======================================================================
        # The overall grade9 should approximately equal the average of the three subjects
        # Target: (mat9 + slo9 + ang9) / 3 ≈ grade9 (within ±1)
        # Most students (75%) will be within ±0.5, almost all (99%+) within ±1
        
        # Calculate current average of the three subjects
        current_avg = (mat9 + slo9 + ang9) / 3
        
        # Calculate difference between target (grade9) and current average
        diff = grade9 - current_avg
        
        # If difference is significant (more than 0.5), adjust all subjects
        if abs(diff) > 0.5:
            # Distribute the difference evenly across all three subjects
            # This preserves the relative differences between subjects
            adjustment = diff / 3
            
            # Apply adjustment and round to integers
            mat9 = round(mat9 + adjustment)
            slo9 = round(slo9 + adjustment)
            ang9 = round(ang9 + adjustment)
            
            # Clamp all subjects back to valid range [2, 5] after adjustment
            mat9 = max(2, min(5, mat9))
            slo9 = max(2, min(5, slo9))
            ang9 = max(2, min(5, ang9))
        
        # STEP 7: Store student data
        # Create a dictionary with all student information
        student = {
            'id': id_student,           # Student ID number
            'grade9': grade9,           # Overall grade (2-5)
            'mat9': mat9,               # Mathematics grade (2-5)
            'slo9': slo9,               # Slovenian grade (2-5)
            'ang9': ang9,               # English grade (2-5)
        }
        
        # Add this student to our data list
        data.append(student)
    
    # Return the complete list of all generated students
    return data
