from Generate_year9 import generate_year9_students
from Generate_year1 import generate_year1_students
import random

def generate_year2_students(year1_data):

    random.seed(2)  # For reproducibility

    """Generate Year 2 data for students who passed Year 1.

    The output list includes only students who passed Year 1 and were not
    expelled, and preserves each student's original ID.
    """

    # Filter: only students who passed Year 1 and weren't expelled
    year1_passed = [s for s in year1_data if s['passed_year1'] and not s['expelled']]
    
    year2_data = []
    students_for_elimination = []

    comp_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}
    award_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}

    for year1_student in year1_passed:

        # YEAR 1 DATA EXTRACTION

        student_id = year1_student["id"]

        # Carry personality from Year 1 with a small drift
        student_personality = random.gauss(year1_student["personality"], 0.1)

        # Adjust personality based on Year 1 experience
        if year1_student["ponavljanje"]:
            # Most retakers become more disciplined, but some become less
            student_personality += random.gauss(-0.1, 0.15) # average shift is negative (more disciplined) but with wide variance to reflect that some students react differently to retaking a year
            #shift = random.gauss(-0.25, 0.30)
        if year1_student["year1_overall"] < 2.5:
            # Low grades: some get motivated, most get discouraged
            student_personality += random.gauss(-0.125, 0.12)
        
        # Year 9 data
        grade9 = year1_student["grade9"]
        mat9 = year1_student["mat9"]
        slo9 = year1_student["slo9"]
        ang9 = year1_student["ang9"]

        # Year 1 data
        year1_overall = year1_student["year1_overall"]
        mat1 = year1_student["mat1"]
        slo1 = year1_student["slo1"]
        ang1 = year1_student["ang1"]

        # Year 2 grades: 5-assessment loop per subject (models multiple tests during the year).
        # Final subject grade = round(average of 5 assessments).
        # Retake is triggered if ANY individual assessment was grade 1, even if the final
        # average rounds to 2 or higher.
        # Subject order is randomised to avoid systematic bias.
        # motivation_boost still applies cross-subject: if a subject had any grade-1 assessment,
        # subsequent subjects get a boost to reduce their grade-1 chance.
        weight_y1 = (year1_overall * 0.85) + (grade9 * 0.15)  # Year 1 overall is the main driver, but year 9 also has some influence
        subjects_order = [('mat', mat1), ('slo', slo1), ('ang', ang1)]
        random.shuffle(subjects_order) # randomise subject order to avoid bias in which subject gets the motivation boost first

        # Add random subject-level shifts so grade distributions vary slightly per run.
        subject_shifts = {
            'mat': random.choice([-0.075, 0.075]),
            'slo': random.choice([-0.075, 0.075]),
            'ang': random.choice([-0.075, 0.075])
        }

        grade2_results = {} # to store final grades for mat2, slo2, ang2
        grade1_count = 0   # subjects that had any grade-1 assessment (drives motivation_boost)
        any_had_grade1 = False  # retake trigger across all subjects

        for subj_name, subj1 in subjects_order: # loop through subjects in random order
            # boost = grade1_count * 0.35 # motivation boost increases by 0.35 for each prior subject that had a grade 1 assessment
            assessments = []
            subj_had_grade1 = False
            for _ in range(5):
                g = grades2(
                    subj1,
                    weight_y1,
                    student_personality,
                    up_shift=(0.05, 0.22),
                    down_shift=(-0.62, 0.30),
                    subject_shift=subject_shifts[subj_name]
                    #motivation_boost=boost
                )
                assessments.append(g)
                if g == 1:
                    subj_had_grade1 = True
            # Final grade = average of 5 assessments
            if subj_had_grade1:
                grade2_results[subj_name] = 1  # retake triggered by any grade-1 assessment, so final grade is set to 1 regardless of average
            else:
                grade2_results[subj_name] = min(5, max(1, round(sum(assessments) / 5)))
            if subj_had_grade1:
                any_had_grade1 = True
                grade1_count += 1

        mat2 = grade2_results['mat']
        slo2 = grade2_results['slo']
        ang2 = grade2_results['ang']
        base2 = (mat2 + slo2 + ang2) / 3

        base = ((year1_overall * 0.88) + (grade9 * 0.12)) * 0.25 + (base2 * 0.75)