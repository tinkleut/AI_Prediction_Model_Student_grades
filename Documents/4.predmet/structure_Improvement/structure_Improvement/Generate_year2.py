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
            student_personality += random.gauss(-0.1, 0.15)
            #shift = random.gauss(-0.25, 0.30)
        if year1_student["year1_overall"] < 2.5:
            # Low grades: some get motivated, most get discouraged
            student_personality += random.gauss(-0.12, 0.1)
        
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
        subjects_order = [('slo', slo1), ('ang', ang1), ('mat', mat1)]
        random.shuffle(subjects_order) # randomise subject order to avoid bias in which subject gets the motivation boost first

        # Add random subject-level shifts so grade distributions vary slightly per run.
        subject_shifts = {
            'mat': random.choice([-0.13, 0.05]),
            'slo': random.choice([-0.05, 0.07]),
            'ang': random.choice([-0.04, 0.06])
        }

        grade2_results = {} # to store final grades for mat2, slo2, ang2
        grade1_count = 0   # subjects that had any grade-1 assessment (drives motivation_boost)
        any_had_grade1 = False  # retake trigger across all subjects
        subj_had_grade1_prev = False
        for subj_name, subj1 in subjects_order: # loop through subjects in random order
            assessments = []
            subj_had_grade1 = False
            for _ in range(5): 
                boost = 0.6 if subj_had_grade1_prev == True else 0.0


                g = grades2(
                    subj1,
                    weight_y1,
                    student_personality,
                    motivation_boost=boost,
                    up_shift=(0.05, 0.2),
                    down_shift=(-0.05, 0.3),
                    subject_shift=subject_shifts[subj_name]
                    
                )
                assessments.append(g)
                if g == 1:
                    subj_had_grade1 = True
                    subj_had_grade1_prev = True
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

        # Calculating competitions
        num_of_comp, list_competitions, list_competitions_nat = competitions(base, comp_counters)

        num_of_awards = awards(base, num_of_comp, list_competitions, list_competitions_nat, award_counters)

        experience_bonus = ((len(list_competitions) - len(list_competitions_nat)) * 0.15) + (len(list_competitions_nat) * 0.25)
        experience_bonus = min(experience_bonus, 5)
        skupno = (base * 0.9) + (experience_bonus * 0.1)

        year2_student = {
            'id': student_id,
            'grade9': grade9,
            'mat9': mat9,
            'slo9': slo9,
            'ang9': ang9,
            'year1_overall': year1_overall,  # carried forward for Year 3 weight
            'mat1': mat1,
            'slo1': slo1,
            'ang1': ang1,
            'mat2': mat2,
            'slo2': slo2,
            'ang2': ang2,
            'base': base,
            'any_had_grade1': any_had_grade1,  # True if any assessment was grade 1
            'num_of_comp': num_of_comp,
            'num_of_awards': num_of_awards,
            'list_competitions': list_competitions,
            'list_competitions_nat': list_competitions_nat,
        }

        year2_data.append(year2_student)

        students_for_elimination.append({
            'id': student_id,
            'skupno': skupno,
            'list_competitions_nat': list_competitions_nat,
            'awards_list': num_of_awards
        })

    # Determine national qualifications once all students have been generated
    qualified_dict = eliminate_students(students_for_elimination)

    for student in year2_data:
        student['qualified_nationals'] = qualified_dict.get(student['id'], [])
        student['num_of_national_comp'] = len(student['qualified_nationals'])

        # National awards for Year 2
        student['national_awards_list'] = national_awards(student['base'], student['qualified_nationals'])
        student['num_of_national_awards'] = len(student['national_awards_list'])

        num_awards = len(student['num_of_awards'])

        # Use the carried-over personality from Year 1 (computed above, lines 28-37)
        personality = student_personality
        student['personality'] = round(personality, 3)

        student['num_of_hours_late_for_class'] = late_for_class(
            student['base'],
            student['num_of_comp'],
            num_awards,
            student['num_of_national_comp'],
            student['num_of_national_awards'],
            personality
        )

        student['num_of_hours_student_was_sent_out'] = hours_sent_out(
            student['base'],
            student['num_of_comp'],
            num_awards,
            student['num_of_national_comp'],
            student['num_of_national_awards'],
            student['num_of_hours_late_for_class'],
            personality
        )

        student['num_of_intentionally_missed_hours'] = intentionally_missed_hours(
            student['base'],
            student['num_of_comp'],
            num_awards,
            student['num_of_national_comp'],
            student['num_of_national_awards'],
            personality
        )

        student['all_missed_hours'] = all_missed(
            student['num_of_hours_late_for_class'],
            student['num_of_hours_student_was_sent_out'],
            student['num_of_intentionally_missed_hours']
        )

        # Unexcused hours are based on a weight combining current base and early-year performance
        sub_base = (student['grade9'] + student['mat9'] + student['slo9'] + student['ang9']) / 4
        weight_for_unexcused = (student['base'] * 0.85) + (sub_base * 0.15) + personality

        student['unexcused_hours_lfc'] = unexcused_hours(
            student['num_of_hours_late_for_class'], weight_for_unexcused, unexcused_late_rates
        )
        student['unexcused_hours_sso'] = unexcused_hours(
            student['num_of_hours_student_was_sent_out'], weight_for_unexcused, unexcused_sent_out_rates
        )
        student['unexcused_hours_imh'] = unexcused_hours(
            student['num_of_intentionally_missed_hours'], weight_for_unexcused, unexcused_missed_rates
        )

        student['all_unexcused_hours'] = (
            student['unexcused_hours_lfc'] +
            student['unexcused_hours_sso'] +
            student['unexcused_hours_imh']
        )

        # Disciplinary warnings and expulsion
        student['num_of_VU'], student['expelled'] = ukori(student['all_unexcused_hours'])

        # Retake logic: triggered if any final grade == 1 OR any individual assessment was grade 1
        year2_avg = (student['mat2'] + student['slo2'] + student['ang2']) / 3
        if year2_avg >= 1.8 and not negativno(student):
            student['ponavljanje'] = False
            student['passed_year2'] = True
        else:
            student['ponavljanje'] = True
            passed, updated_grades = ponavljanje(student, student['base'])
            student['passed_year2'] = passed
            student['mat2'] = updated_grades['mat2']
            student['slo2'] = updated_grades['slo2']
            student['ang2'] = updated_grades['ang2']

        student['grade2'] = student['passed_year2']
        student['year2_overall'] = year2_overall(student)

    return year2_data
        

# HELPER FUNCTIONS

# Direct failure probability: base -> chance of getting grade 1 regardless of normal shift.
# Accounts for unexpected catastrophic failure (illness, stress, bad exam day).
# motivation_boost (added to base) reduces this probability for students who already have a grade 1.
failure_probs = [
    (2.0, 0.017),
    (2.3, 0.012),
    (2.6, 0.008),
    (3.0, 0.004),
    (3.5, 0.002),
    (4.0, 0.001),
    (float("inf"), 0.0003)
]

# Probability table: base value -> probability that the student does well (maintains/improves).
# Weak students rarely do well; strong students usually maintain.
good_outcome_probs = [
    (1.8, 0.05),
    (2.0, 0.15),
    (2.3, 0.28),
    (2.5, 0.48),
    (2.8, 0.68),
    (3.0, 0.80),
    (3.3, 0.87),
    (3.5, 0.92),
    (3.8, 0.95),
    (4.0, 0.97),
    (float("inf"), 0.99)
]

def grades2(subject1, weight_year1, student_personality, up_shift=(0.05, 0.22), down_shift=(-0.20, 0.20), vlo_down_shift=(-0.15, 0.12), motivation_boost=0.0, subject_shift=0.0, ponavljanje=False):
    """
    Generate a Year 2 subject grade.
    - up_shift:        (mean, std) applied when student does well
    - down_shift:      (mean, std) applied when student struggles (base >= 2.3)
    - vlo_down_shift:  (mean, std) applied when weakest students struggle (base < 2.3)
    - motivation_boost: added to base before all calculations; used to reduce chance of
                        a second/third grade 1 (0.35 per prior grade 1 in same student).
    - subject_shift:   small subject-specific run-dependent shift to add grade variation.
    """
    base = (subject1 * 0.3) + (weight_year1 * 0.7) + motivation_boost + subject_shift

    if ponavljanje:
        shift = random.gauss(-0.35, 0.30)
    else:
        # Look up probability of doing well based on the student's base
        good_chance = 0.50
        for limit, probability in good_outcome_probs:
            if base <= limit:
                good_chance = probability
                break

        # Check for direct failure first (illness, stress, catastrophic exam)
        fail_chance = 0.0
        for limit, prob in failure_probs:
            if base <= limit:
                fail_chance = prob
                break
        if random.random() < fail_chance:
            return 1  # Direct grade 1 — motivation_boost already reduced base so this is rare for 2nd/3rd subject

        if random.random() < good_chance:
            shift = random.gauss(up_shift[0], up_shift[1])         # Student does well
        elif base < 2.3:
            shift = random.gauss(vlo_down_shift[0], vlo_down_shift[1])  # Weakest struggle hard -> grade 1
        else:
            shift = random.gauss(down_shift[0], down_shift[1])     # Others struggle -> grade 2

    grade2 = min(5, max(1, round(base + shift + student_personality * 0.25)))
    return grade2


weight_probs = [
    (2.0, 0.001),  # Dvignemo spodnji prag
    (2.5, 0.005), 
    (3.0, 0.010),
    (3.5, 0.030),  # Več ljudi se premakne v sredino
    (3.8, 0.060),
    (4.0, 0.100),
    (4.2, 0.140),  # Opazno povečanje verjetnosti za dobre rezultate
    (4.4, 0.180),
    (4.5, 0.230),
    (4.7, 0.350),  # Velik skok za elito
    (4.85, 0.520), # Večja verjetnost za vrhunske rezultate
    (float("inf"), 0.550) 
]

def competitions(base, comp_counters):

    list_competitions = []
    list_competitions_nat = []

    # Competitions 3, 5, 8 do NOT lead to nationals
    competitions_with_nationals = {1, 2, 4, 6, 7, 9, 10} 

    for i in range(1, 11):
        # Determine probability from lookup table
        for limit, probability in weight_probs:
            if base <= limit:
                entered = random.random() < probability
                break

        if entered:
            list_competitions.append(str(i))

            if i in competitions_with_nationals:
                list_competitions_nat.append(str(i))
                comp_counters[i] += 1

    return len(list_competitions), list_competitions, list_competitions_nat


award_probs = [
    (1.8, 0.003),
    (2.0, 0.008),
    (2.3, 0.012),
    (2.5, 0.020),
    (2.8, 0.030),
    (3.0, 0.045),
    (3.3, 0.065),
    (3.5, 0.090),
    (3.8, 0.120),
    (4.0, 0.150),
    (4.2, 0.200),
    (4.4, 0.220),
    (4.5, 0.330),
    (4.7, 0.400),
    (4.85, 0.480),
    (float("inf"), 0.550)
]

def awards(base, num_of_comp, list_competitions, list_competitions_nat, award_counters):
    if num_of_comp == 0:
        return []

    experience_bonus = ((len(list_competitions) - len(list_competitions_nat)) * 0.15) + (len(list_competitions_nat) * 0.25) 
    experience_bonus = min(experience_bonus, 5)
    skupno = (base * 0.9) + (experience_bonus * 0.1)
    awards_list = []

    for comp in list_competitions:
        comp_id = int(comp)
        # Determine probability from lookup table
        for limit, probability in award_probs:
            if skupno <= limit:
                awd = random.random() < probability
                break

        if awd:
            awards_list.append(comp)
            if comp_id in award_counters:
                award_counters[comp_id] += 1

    return awards_list

def eliminate_students(all_students_data):
    """
    For each competition with nationals (1, 2, 4, 6, 7, 9, 10),
    determine who qualifies for nationals based on:
    1. National capacity = 25% of students who ENTERED the competition
    2. Only award winners can qualify
    3. If award winners exceed capacity, rank by skupno and take top N
    4. If award winners < capacity, all award winners qualify
    
    Example:
    - 1000 students enter competition
    - Capacity = 250 spots (25% of 1000)
    - 400 students win awards
    - Top 250 (by skupno) of those 400 qualify for nationals
    - Other 150 keep their awards but don't go to nationals
    
    Parameters:
        all_students_data: List of student dictionaries with:
            - 'id': student ID
            - 'skupno': award ability score (weight + experience)
            - 'list_competitions_nat': competitions with nationals they entered
            - 'awards_list': awards they won
    
    Returns:
        dict: {student_id: [list of comp_ids they qualified for nationals]}
    """
    # Track total participants (who entered) per competition
    comp_total_participants = {
        1: 0,
        2: 0,
        4: 0,
        6: 0,
        7: 0,
        9: 0,
        10: 0
    }
    
    # Track award winners per competition
    comp_award_winners = {
        1: [],
        2: [],
        4: [],
        6: [],
        7: [],
        9: [],
        10: []
    }
    
    # First pass: count total participants who entered each competition
    for student in all_students_data:
        list_competitions_nat = student['list_competitions_nat']
        
        for comp_id_str in list_competitions_nat:
            comp_id = int(comp_id_str)
            if comp_id in [1, 2, 4, 6, 7, 9, 10]:
                comp_total_participants[comp_id] += 1
    
    # Second pass: collect award winners for each competition
    for student in all_students_data:
        student_id = student['id']
        skupno = student['skupno']
        awards_list = student.get('awards_list', [])
        
        # For each award they won, add them to that competition's award winners
        for award_comp_id_str in awards_list:
            comp_id = int(award_comp_id_str)
            
            # Only track competitions with nationals
            if comp_id in [1, 2, 4, 6, 7, 9, 10]:
                comp_award_winners[comp_id].append((student_id, skupno))
    
    # For each competition, determine who qualifies for nationals
    qualified_for_nationals = {}
    
    for comp_id in [1, 2, 4, 6, 7, 9, 10]:
        total_participants = comp_total_participants[comp_id]
        award_winners = comp_award_winners[comp_id]
        
        if not award_winners:
            continue  # No one won awards in this competition
        
        # Calculate capacity: 25% of students who entered the competition
        capacity = int(total_participants * 0.25)
        capacity = max(1, capacity)  # At least 1 spot if anyone entered
        
        # Sort award winners by ability score (highest first)
        award_winners.sort(key=lambda x: x[1], reverse=True)
        
        # Determine how many qualify: min of (award winners count, capacity)
        num_qualifiers = min(len(award_winners), capacity)
        
        # Select qualifiers
        for i in range(num_qualifiers):
            student_id = award_winners[i][0]
            
            # Add to qualified list
            if student_id not in qualified_for_nationals:
                qualified_for_nationals[student_id] = []
            qualified_for_nationals[student_id].append(comp_id)
    
    return qualified_for_nationals

national_award_probs = [
    (1.8, 0.0003),
    (2.0, 0.0005),
    (2.3, 0.001),
    (2.5, 0.002),
    (2.8, 0.004),
    (3.0, 0.006),
    (3.3, 0.010),
    (3.5, 0.015),
    (3.8, 0.025),
    (4.0, 0.040),
    (4.2, 0.060),
    (4.4, 0.090),
    (4.5, 0.180),
    (4.7, 0.220),
    (4.85, 0.280),
    (float("inf"), 0.350)
]

def national_awards(base, qualified_nationals):
    """
    Calculate awards won at national competitions.
    Nationals are MUCH HARDER than regional competitions.
    Only students who qualified (top 25% of award winners) can compete here.
    """
    if not qualified_nationals:
        return []
        
    national_awards_list = []
    
    for comp_id in qualified_nationals:
        for limit, probability in national_award_probs:
            if base <= limit:
                won_award = random.random() < probability
                break

        if won_award:
            national_awards_list.append(str(comp_id))
    
    return national_awards_list

# Weight-to-probability lookup for being late to class
# 4.5+: almost never | 4.5→3.0: linear | 3.0→2.5: steeper | 2.5→2.0: steeper | <2.0: steepest
late_probs = [
    (1.0, 0.070),
    (1.3, 0.050),
    (1.5, 0.035),
    (1.8, 0.020),
    (2.0, 0.012),
    (2.3, 0.005),
    (2.5, 0.003),
    (2.8, 0.0015),
    (3.0, 0.0008),
    (3.3, 0.0004),
    (3.5, 0.0002),
    (3.8, 0.0001),
    (4.0, 0.00005),
    (4.5, 0.00002),
    (float("inf"), 0.000005)
]

def late_for_class(base , num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_late_class = 0

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (base * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.05, 0.05])

    # Resolve probability once (weight is constant across all iterations)
    # Limit, probibility is a pair in late_probs
    late_chance = 0.0005
    for limit, probability in late_probs:
        if weight <= limit:
            late_chance = probability
            break

    for days in range(150):
        for hours in range(7):
            if random.random() < late_chance:
                num_late_class += 1


    return num_late_class

# Weight-to-probability lookup for being sent out of class
# 100% unexcused! 4.5+: almost never | 4.5→3.0: linear | steeper steps below 3.0, 2.5, 2.0
sent_out_probs = [
    (1.0, 0.008),
    (1.3, 0.005),
    (1.5, 0.003),
    (1.8, 0.0015),
    (2.0, 0.0008),
    (2.3, 0.0003),
    (2.5, 0.00015),
    (2.8, 0.00006),
    (3.0, 0.00002),
    (3.5, 0.000005),
    (float("inf"), 0.000001)
]

# Lateness-to-multiplier lookup for sent out probability
lateness_multipliers = [
    (15, 1.0),
    (25, 1.1),
    (40, 1.3),
    (60, 1.5),
    (float("inf"), 1.8)
]

def hours_sent_out(base, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, num_late_class, personality=0):
    num_sent_out = 0

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (base * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.02, 0.02])

    # Resolve lateness multiplier
    lateness_multiplier = 1.8
    for limit, multiplier in lateness_multipliers:
        if num_late_class < limit:
            lateness_multiplier = multiplier
            break

    # Resolve base probability once (weight is constant across all iterations)
    base_chance = 0.0001
    for limit, probability in sent_out_probs:
        if weight <= limit:
            base_chance = probability
            break

    sent_out_chance = base_chance * lateness_multiplier

    for days in range(180):
        for hours in range(6):
            if random.random() < sent_out_chance:
                num_sent_out += 1

    return num_sent_out

# Weight-to-probability lookup for intentionally skipping class
# 4.5+: almost never | 4.5→3.0: linear | 3.0→2.5: steeper | 2.5→2.0: steeper | <2.0: steepest
skip_probs = [
    (1.0, 0.14),
    (1.3, 0.09),
    (1.5, 0.06),
    (1.8, 0.038),
    (2.0, 0.025),
    (2.3, 0.018),
    (2.5, 0.013),
    (2.8, 0.009),
    (3.0, 0.006),
    (3.3, 0.003),
    (3.5, 0.0015),
    (3.8, 0.0007),
    (4.0, 0.0003),
    (4.5, 0.0001),
    (float("inf"), 0.00003)
]

def intentionally_missed_hours(base, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_missed = 0

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (base * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.05, 0.05])

    # Resolve probability once (weight is constant across all iterations)
    skip_chance = 0.005
    for limit, probability in skip_probs:
        if weight <= limit:
            skip_chance = probability
            break

    for days in range(180):
        for hours in range(6):
            if random.random() <= skip_chance:
                num_missed += 1
    
    return num_missed


def all_missed(num_of_hours_late_for_class, num_of_hours_student_was_sent_out, num_of_intentionally_missed_hours):
    return num_of_hours_late_for_class + num_of_hours_student_was_sent_out + num_of_intentionally_missed_hours


# Unexcused rate lookups: weight → fraction of hours that end up unexcused
# Lower weight (weaker students) → higher unexcused rate

# Late for class: 1-4% unexcused (almost always excused with a parent note)
unexcused_late_rates = [
    (1.8, 0.04),
    (2.0, 0.035),
    (2.3, 0.03),
    (2.5, 0.025),
    (2.8, 0.02),
    (3.0, 0.018),
    (3.3, 0.015),
    (3.5, 0.013),
    (3.8, 0.011),
    (4.0, 0.010),
    (4.2, 0.008),
    (4.5, 0.006),
    (4.7, 0.005),
    (5.0, 0.004),
    (float("inf"), 0.003)
]

# Sent out: 100% unexcused (teacher sent you out, no excuse possible)
unexcused_sent_out_rates = [
    (float("inf"), 1.0)
]

# Intentionally missed: 0.5-3% unexcused (students almost always get a parent/doctor note)
unexcused_missed_rates = [
    (1.8, 0.03),
    (2.0, 0.025),
    (2.5, 0.02),
    (3.0, 0.015),
    (3.5, 0.01),
    (4.0, 0.007),
    (float("inf"), 0.005)
]

def unexcused_hours(total_hours, weight, rate_table):
    """
    Given total hours and a student's weight, determine how many are unexcused.
    Each hour is independently rolled against the unexcused rate.
    """
    # Resolve unexcused rate from lookup table
    rate = 0.15
    for limit, r in rate_table:
        if weight <= limit:
            rate = r
            break
    
    unexcused = 0
    for _ in range(int(total_hours)):
        if random.random() < rate:
            unexcused += 1
    
    return unexcused

def ukori(all_unexcused_hours):
    """
    Calculate disciplinary warnings (vzgojni ukori / VU) based on unexcused hours.
    Every 10 unexcused hours = 1 ukor.
    4 ukors = expelled (izključen).
    Returns (num_of_VU, expelled)
    """
    num_of_VU = int(all_unexcused_hours // 10)
    expelled = num_of_VU >= 4
    return num_of_VU, expelled


def year2_overall(student):
    """Calculate the overall Year 2 score.
    90% grades, 10% everything else (competitions, awards, behavior).
    Returns a value on a 1-5 scale.
    """
    grade_avg = (student['mat2'] + student['slo2'] + student['ang2']) / 3
    
    # "Everything else" score on a 1-5 scale
    # Start at 3.0 (neutral), adjust based on extracurriculars and behavior
    extra = 3.0
    extra += student['num_of_comp'] * 0.2
    num_awards = len(student['num_of_awards'])
    extra += num_awards * 0.3
    extra += student.get('num_of_national_comp', 0) * 0.3
    extra += student.get('num_of_national_awards', 0) * 0.5
    extra -= student.get('all_unexcused_hours', 0) * 0.05
    extra -= student.get('num_of_VU', 0) * 0.5
    extra = min(5.0, max(1.0, extra))
    
    overall = (grade_avg * 0.9) + (extra * 0.1)
    return round(overall, 2)


def ponavljanje(student, base):
    """Handle retaking (ponavljanje) for students with grade 1.
    - If ALL 3 subjects are 1 → automatic fail, no retake.
    - If 1-2 subjects are 1 → 2 retake attempts per subject.
      Each attempt has a probability of passing (getting a 2).
    Returns (passed, updated_grades) where updated_grades is a dict of {subject: new_grade}.
    """
    subjects = {'mat2': student['mat2'], 'slo2': student['slo2'], 'ang2': student['ang2']}
    failed_subjects = [sub for sub, grade in subjects.items() if grade == 1]
    
    # No failed subjects → no retake needed
    if len(failed_subjects) == 0:
        return True, subjects
    
    # All 3 failed → no retake allowed, automatic fail
    if len(failed_subjects) == 3:
        return False, subjects
    
    # 1-2 failed subjects → 2 retake attempts each
    # ~90% of retakers should pass: same logic as Year 1.
    # base ~2 → 75% per attempt (93% in 2 attempts)
    # base ~3 → 85% per attempt (98% in 2 attempts)
    # base ~4 → 95% per attempt (100% in 2 attempts)
    pass_chance = min(0.55, max(0.20, (base - 1) * 0.03 + 0.65))
    
    updated = dict(subjects)
    for sub in failed_subjects:
        passed_retake = False
        for attempt in range(2):
            if random.random() < pass_chance:
                passed_retake = True
                updated[sub] = 2  # Minimum passing grade
                break
        if not passed_retake:
            return False, updated
    
    return True, updated


def naredil(student):
    """Check if a student passed Year 2 directly (all grades >= 2).
    Returns True if the student goes to the next year, False otherwise.
    """
    return student['mat2'] >= 2 and student['slo2'] >= 2 and student['ang2'] >= 2


def negativno(student):
    """Check if a student has a grade of 1 in any subject (failed).
    Returns True if the student has at least one grade of 1, False otherwise.
    """
    return student['mat2'] == 1 or student['slo2'] == 1 or student['ang2'] == 1
