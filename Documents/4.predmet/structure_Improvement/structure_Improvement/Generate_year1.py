from Generate_year9 import generate_year9_students
import random

# STUDENT DATA GENERATOR FOR YEAR 1 (HIGH SCHOOL)
# This file generates Year 1 (high school) data based on Year 9 students.
# Each Year 1 student is the same person from Year 9, just progressed forward.

def generate_year1_students(year9_data):

    random.seed(2)  # Set seed for reproducibility

    # Counters passed to competitions() and awards() instead of globals
    comp_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}
    award_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}
    
    year1_data = []
    students_for_elimination = []  # Collect data for national awards
    
    for year9_student in year9_data:
        # Extract Year 9 data
        id_student = year9_student['id']
        grade9 = year9_student['grade9']
        mat9 = year9_student['mat9']
        slo9 = year9_student['slo9']
        ang9 = year9_student['ang9']
        
        # Add random variation for subject grade balances
        # This will randomly shift a few percent between adjacent grades
        english_shift = random.choice([-0.05, 0.05])  # English: grade 3 vs 4
        slovenian_shift = random.choice([-0.05, 0.05])  # Slovenian: grade 3 vs 4  
        math_shift = random.choice([-0.05, 0.05])  # Math: grade 2 vs 3 (with bias toward 3)

        # Generate Year 1 grades - 4-tier adaptive shift (thresholds: 2.3 / 3.0 / 4.2)
        # Each subject has a distinct mid-tier pull:
        #   Math (-0.55):    most grade3-heavy, least grade4
        #   Slovenian (-0.52): slightly less grade3 than math
        #   English (-0.42):   slightly less grade3 than Slovenian (~1% diff), most grade4
        mat1_base = weight_sub_grade(grade9, mat9) + noise_grade(mat9)
        if   mat1_base < 2.3:
            mat1_base += random.gauss(-0.28 + math_shift, 0.20)
        elif mat1_base < 3.0:
            mat1_base += random.gauss(-0.18 + math_shift, 0.16)
        elif mat1_base < 4.2:
            mat1_base += random.gauss(-0.24 + math_shift, 0.24)
        else:
            mat1_base += random.gauss(-0.28 + math_shift, 0.28)
        mat1 = min(5, max(1, round(mat1_base))) # Pomembno
        
        slo1_base = weight_sub_grade(grade9, slo9) + noise_grade(slo9)
        if   slo1_base < 2.3:
            slo1_base += random.gauss(-0.21 + slovenian_shift, 0.20)
        elif slo1_base < 3.0:
            slo1_base += random.gauss(-0.14 + slovenian_shift, 0.16)
        elif slo1_base < 4.2:
            slo1_base += random.gauss(-0.24 + slovenian_shift, 0.24)
        else:
            slo1_base += random.gauss(-0.28 + slovenian_shift, 0.28)
        slo1 = min(5, max(1, round(slo1_base))) # Pomembno
        
        ang1_base = weight_sub_grade(grade9, ang9) + noise_grade(ang9)
        if   ang1_base < 2.3:
            ang1_base += random.gauss(-0.21 + english_shift, 0.18)
        elif ang1_base < 3.0:
            ang1_base += random.gauss(-0.14 + english_shift, 0.16)
        elif ang1_base < 4.2:
            ang1_base += random.gauss(-0.24 + english_shift, 0.25)
        else:
            ang1_base += random.gauss(-0.28 + english_shift, 0.28)
        ang1 = min(5, max(1, round(ang1_base))) # Pomembno

        num_of_comp, list_competitions, list_competitions_nat = competitions(grade9, mat1, ang1, slo1, mat9, slo9, ang9, comp_counters)
        
        num_of_awards = awards(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_of_comp, list_competitions, list_competitions_nat, award_counters)
        
        # Calculate skupno score for elimination (same logic as awards function)
        base = (mat1 + slo1 + ang1) / 3
        second_base = (grade9 + mat9 + slo9 + ang9) / 4
        weight = (base * 0.85) + (second_base * 0.15)
        experience_bonus = ((len(list_competitions) - len(list_competitions_nat)) * 0.15) + (len(list_competitions_nat) * 0.25)
        experience_bonus = min(experience_bonus, 5)
        skupno = (weight * 0.9) + (experience_bonus * 0.1)
        
        year1_student = {
            'id': id_student,
            'mat1': mat1,
            'slo1': slo1,
            'ang1': ang1,
            'grade9': grade9,
            'mat9': mat9,
            'slo9': slo9,
            'ang9': ang9,
            'num_of_comp': num_of_comp,
            'num_of_awards': num_of_awards,
            'list_competitions': list_competitions,
            'list_competitions_nat': list_competitions_nat,
        }
     
        year1_data.append(year1_student)
        
        # Collect data for elimination
        students_for_elimination.append({
            'id': id_student,
            'skupno': skupno,
            'list_competitions_nat': list_competitions_nat,
            'awards_list': num_of_awards
        })
    
    # Run elimination to find who qualifies for nationals (top 25% per competition)
    qualified_dict = eliminate_students(students_for_elimination)
    
    # Add qualification data and calculate national awards for each student
    # student is an index(i)
    for student in year1_data:
        student['qualified_nationals'] = qualified_dict.get(student['id'], [])
        
        # Calculate national awards for students who qualified
        if student['qualified_nationals']:
            national_awards_list = national_awards(
                student['grade9'],
                student['mat1'],
                student['slo1'],
                student['ang1'],
                student['mat9'],
                student['slo9'],
                student['ang9'],
                student['qualified_nationals']
            )
            student['national_awards_list'] = national_awards_list
        else:
            student['national_awards_list'] = []
        
        # Update the num fields that were set to None earlier (lines 70-71)
        student['num_of_national_comp'] = len(student['qualified_nationals'])
        student['num_of_national_awards'] = len(student['national_awards_list'])
        
        # Now calculate late hours and sent out hours (needs nationals data)
        num_awards = len(student['num_of_awards'])
        
        # Per-student personality offset: some low-grade students are disciplined,
        # some high-grade students are sloppy. Applied to weight in all behavior functions.
        personality = random.gauss(0, 0.3)
        student['personality'] = round(personality, 3)
        
        student['num_of_hours_late_for_class'] = late_for_class(
            student['grade9'],
            student['mat1'],
            student['slo1'],
            student['ang1'],
            student['mat9'],
            student['slo9'],
            student['ang9'],
            student['num_of_comp'],
            num_awards,
            student['num_of_national_comp'],
            student['num_of_national_awards'],
            personality
        )
        
        student['num_of_hours_student_was_sent_out'] = hours_sent_out(
            student['grade9'],
            student['mat1'],
            student['slo1'],
            student['ang1'],
            student['mat9'],
            student['slo9'],
            student['ang9'],
            student['num_of_comp'],
            num_awards,
            student['num_of_national_comp'],
            student['num_of_national_awards'],
            student['num_of_hours_late_for_class'],
            personality
        )
        
        student['num_of_intentionally_missed_hours'] = intentionally_missed_hours(
            student['grade9'],
            student['mat1'],
            student['slo1'],
            student['ang1'],
            student['mat9'],
            student['slo9'],
            student['ang9'],
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
        
        # Calculate unexcused hours for each type
        base = (student['mat1'] + student['slo1'] + student['ang1']) / 3
        sub_base = (student['grade9'] + student['mat9'] + student['slo9'] + student['ang9']) / 4
        weight_for_unexcused = (base * 0.85) + (sub_base * 0.15) + personality
        
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
        
        # Calculate disciplinary warnings (ukori)
        student['num_of_VU'], student['expelled'] = ukori(student['all_unexcused_hours'])
        
        # Determine if student passed directly or needs retake
        year1_avg = (student['mat1'] + student['slo1'] + student['ang1']) / 3
        if year1_avg >= 1.8 and not negativno(student):
            student['ponavljanje'] = False
            student['passed_year1'] = True
        else:
            student['ponavljanje'] = True
            passed, updated_grades = ponavljanje(student)
            student['passed_year1'] = passed
            # Update grades if retake changed them
            student['mat1'] = updated_grades['mat1']
            student['slo1'] = updated_grades['slo1']
            student['ang1'] = updated_grades['ang1']
        
        student['grade1'] = student['passed_year1']
        student['year1_overall'] = year1_overall(student)
    
    return year1_data


# HELPER FUNCTIONS

# I will use this in the next year to make it be a bit more random!
def noise_grade(grade):
    grade_ranges = {
        5: (0.2, 0.35),
        4: (0.2, 0.40),
        3: (0.3, 0.65),   
        2: (0.08, 0.30),
        1: (0.15, 0.45)
    }

    low, high = grade_ranges.get(grade, (0.15, 0.45))
    noise_std = random.uniform(low, high)

    return random.gauss(0, noise_std)

def weight_sub_grade(grade, subject):
    # 0.7 weight on overall grade9, 0.3 on specific subject9:
    # overall academic ability matters more than subject-specific Y9 score.
    # This breaks the grade-2 floor effect caused by Y9 subject minimum of 2.
    base = (grade * 0.7) + (subject * 0.3)
    return base


# Weight-to-probability lookup for competition entry
weight_probs = [
    (1.8, 0.001),
    (2.0, 0.003),
    (2.3, 0.005),
    (2.5, 0.008),
    (2.8, 0.010),
    (3.0, 0.013),
    (3.3, 0.018),
    (3.5, 0.025),
    (3.8, 0.045),
    (4.0, 0.075),
    (4.2, 0.100),
    (4.4, 0.120),
    (4.5, 0.170),
    (4.7, 0.250),
    (4.85, 0.500),
    (float("inf"), 0.550)
]

def competitions(grade9, mat1, ang1, slo1, mat9, slo9, ang9, counters):
    base = (mat1 + slo1 + ang1) / 3
    second_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight = (base * 0.8) + (second_base * 0.2)

    list_competitions = []
    list_competitions_nat = []

    # Competitions 3, 5, 8 do NOT lead to nationals
    competitions_with_nationals = {1, 2, 4, 6, 7, 10}

    for i in range(1, 11):
        # Determine probability from lookup table
        for limit, probability in weight_probs:
            if weight <= limit:
                entered = random.random() < probability
                break

        if entered:
            list_competitions.append(str(i))

            if i in competitions_with_nationals:
                list_competitions_nat.append(str(i))
                counters[i] += 1

    return len(list_competitions), list_competitions, list_competitions_nat


# Weight-to-probability lookup for award winning
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
    (4.0, 0.180),
    (4.2, 0.250),
    (4.4, 0.290),
    (4.5, 0.360),
    (4.7, 0.480),
    (4.85, 0.530),
    (float("inf"), 0.580)
]

def awards(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_of_comp, list_competitions, list_competitions_nat, counters):
    if num_of_comp == 0:
        return []

    base = (mat1 + slo1 + ang1) / 3
    second_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight = (base * 0.85) + (second_base * 0.15)
    experience_bonus = ((len(list_competitions) - len(list_competitions_nat)) * 0.15) + (len(list_competitions_nat) * 0.25) 
    experience_bonus = min(experience_bonus, 5)
    skupno = (weight * 0.85) + (experience_bonus * 0.15)

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
            if comp_id in counters:
                counters[comp_id] += 1

    return awards_list


# A.I.        
def eliminate_students(all_students_data):
    """
    For each competition with nationals (1, 2, 4, 6, 7, 10),
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
        10: 0
    }
    
    # Track award winners per competition
    comp_award_winners = {
        1: [],
        2: [],
        4: [],
        6: [],
        7: [],
        10: []
    }
    
    # First pass: count total participants who entered each competition
    for student in all_students_data:
        list_competitions_nat = student['list_competitions_nat']
        
        for comp_id_str in list_competitions_nat:
            comp_id = int(comp_id_str)
            if comp_id in [1, 2, 4, 6, 7, 10]:
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
            if comp_id in [1, 2, 4, 6, 7, 10]:
                comp_award_winners[comp_id].append((student_id, skupno))
    
    # For each competition, determine who qualifies for nationals
    qualified_for_nationals = {}
    
    for comp_id in [1, 2, 4, 6, 7, 10]:
        total_participants = comp_total_participants[comp_id]
        award_winners = comp_award_winners[comp_id]
        
        if not award_winners:
            continue  # No one won awards in this competition
        
        # Calculate capacity: 20% of students who entered the competition
        capacity = int(total_participants * 0.20)
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

# Weight-to-probability lookup for national award winning (much harder than regional)
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

def national_awards(grade9, mat1, slo1, ang1, mat9, slo9, ang9, qualified_nationals):
    """
    Calculate awards won at national competitions.
    Nationals are MUCH HARDER than regional competitions.
    Only students who qualified (top 25% of award winners) can compete here.
    """
    if not qualified_nationals:
        return []
    
    # Calculate ability score for nationals
    base = (mat1 + slo1 + ang1) / 3
    sub_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight = (base * 0.9) + (sub_base * 0.1)  # Nationals weight Year 1 grades more heavily
    
    national_awards_list = []
    
    for comp_id in qualified_nationals:
        for limit, probability in national_award_probs:
            if weight <= limit:
                won_award = random.random() < probability
                break

        if won_award:
            national_awards_list.append(str(comp_id))
    
    return national_awards_list


# Weight-to-probability lookup for being late to class
# 4.5+: almost never | 4.5→3.0: linear | 3.0→2.5: steeper | 2.5→2.0: steeper | <2.0: steepest
late_probs = [
    (1.3, 0.0500), # 7%
    (1.5, 0.0430), # 10%
    (1.8, 0.0350), # 8.5%
    (2.0, 0.0210), # 7%
    (2.3, 0.0150), # 5.5%
    (2.5, 0.0090), # 4.5%
    (2.8, 0.0055), # 3.5%
    (3.0, 0.0030), # 2.5% 
    (3.3, 0.0017), # 1.8%
    (3.5, 0.00010), # 1.2%
    (3.8, 0.0006), # 0.8%
    (4.0, 0.0004), # 0.5%
    (4.5, 0.0002), # 0.2% 
    (float("inf"), 0.0001) # 0.1% 
]

def late_for_class(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_late_class = 0

    base = (mat1 + slo1 + ang1) / 3
    sub_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight_grade = (base * 0.85) + (sub_base * 0.15)

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (weight_grade * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.05, 0.05])

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
    (1.0, 0.0055),
    (1.3, 0.005),
    (1.5, 0.004),
    (1.8, 0.002),
    (2.0, 0.0007),
    (2.3, 0.0002),
    (2.5, 0.000012),
    (2.8, 0.0000015),
    (3.0, 0.0000007),
    (3.5, 0.0000005),
    (3.8, 0.0000004),
    (4.0, 0.0000003),
    (4.5, 0.0000002),
    (float("inf"), 0.00000001)
]

# Lateness-to-multiplier lookup for sent out probability
lateness_multipliers = [
    (15, 1.0),
    (25, 1.1),
    (40, 1.2),
    (60, 1.4),
    (float("inf"), 1.6)
]

def hours_sent_out(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, num_late_class, personality=0):
    num_sent_out = 0

    base = (mat1 + slo1 + ang1) / 3
    sub_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight_grade = (base * 0.85) + (sub_base * 0.15)

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (weight_grade * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.02, 0.02])

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
    (1.2, 0.0820),     # ~124 hrs avg — unicorn, weight almost unreachable
    (1.5, 0.0690),     # ~108 hrs avg — extremely rare
    (1.8, 0.0380),     # ~92 hrs avg  — chronic skipper
    (2.0, 0.0220),     # ~70 hrs avg
    (2.3, 0.0160),     # ~43 hrs avg
    (2.5, 0.0065),     # ~19 hrs avg  — middle group upper
    (2.8, 0.0030),     # ~13 hrs avg  — middle group
    (3.0, 0.0012),     # ~9 hrs avg
    (3.3, 0.0009),     # ~5 hrs avg
    (3.5, 0.0007),     # ~3 hrs avg
    (3.8, 0.0005),     # ~2 hrs avg
    (4.0, 0.0003),     # ~1 hr avg    — good students
    (4.2, 0.00005),    # ~0.5 hrs avg
    (4.5, 0.00002),    # ~0.2 hrs avg
    (float("inf"), 0.00001)  # near-perfect attendance
]

def intentionally_missed_hours(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_missed = 0

    base = (mat1 + slo1 + ang1) / 3
    sub_base = (grade9 + mat9 + slo9 + ang9) / 4
    weight_grade = (base * 0.85) + (sub_base * 0.15)

    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight_comp = (base_reg * 0.20) + (base_nat * 0.80)

    weight = (weight_grade * 0.75) + (weight_comp * 0.25) + personality + random.choice([-0.05, 0.05])

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
    (1.3, 0.11),
    (1.5, 0.09),
    (1.8, 0.07),
    (2.0, 0.05),
    (2.3, 0.04),
    (2.5, 0.03),
    (2.8, 0.019),
    (3.0, 0.017),
    (3.3, 0.015),
    (3.5, 0.013),
    (3.8, 0.011),
    (4.0, 0.009),
    (4.2, 0.0065),
    (4.5, 0.0045),
    (4.7, 0.0035),
    (float("inf"), 0.002)
]

# Sent out: 100% unexcused (teacher sent you out, no excuse possible)
unexcused_sent_out_rates = [
    (float("inf"), 1.0)
]

# Intentionally missed: 0.5-3% unexcused (students almost always get a parent/doctor note)
unexcused_missed_rates = [
    (1.3, 0.10),
    (1.5, 0.08),
    (1.8, 0.06),
    (2.0, 0.04),
    (2.5, 0.03),
    (3.0, 0.0175),
    (3.5, 0.012),
    (4.0, 0.008),
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


def year1_overall(student):
    """Calculate the overall Year 1 score.
    90% grades, 10% everything else (competitions, awards, behavior).
    Returns a value on a 1-5 scale.
    """
    grade_avg = (student['mat1'] + student['slo1'] + student['ang1']) / 3
    
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
    return round(overall)


def ponavljanje(student):
    """Handle retaking (ponavljanje) for students with grade 1.
    - If ALL 3 subjects are 1 → automatic fail, no retake.
    - If 1-2 subjects are 1 → 2 retake attempts per subject.
      Each attempt has a probability of passing (getting a 2).
    Returns (passed, updated_grades) where updated_grades is a dict of {subject: new_grade}.
    """
    subjects = {'mat1': student['mat1'], 'slo1': student['slo1'], 'ang1': student['ang1']}
    failed_subjects = [sub for sub, grade in subjects.items() if grade == 1]
    
    # No failed subjects → no retake needed
    if len(failed_subjects) == 0:
        return True, subjects
    
    # All 3 failed → no retake allowed, automatic fail
    if len(failed_subjects) == 3:
        return False, subjects
    
    # 1-2 failed subjects → 2 retake attempts each
    # ~90% of retakers should pass: pass_chance is high to reflect that students
    # who only barely failed can usually pass a retake exam.
    base = (student['grade9'] + student['mat9'] + student['slo9'] + student['ang9']) / 4
    pass_chance = min(0.55, max(0.20, (base - 1) * 0.03 + 0.45))
    
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
    """Check if a student passed Year 1 directly (all grades >= 2).
    Returns True if the student goes to the next year, False otherwise.
    """
    return student['mat1'] >= 2 and student['slo1'] >= 2 and student['ang1'] >= 2

def negativno(student):
    """Check if a student has a grade of 1 in any subject (failed).
    Returns True if the student has at least one grade of 1, False otherwise.
    """
    return student['mat1'] == 1 or student['slo1'] == 1 or student['ang1'] == 1
