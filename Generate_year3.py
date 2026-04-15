from Generate_year9 import generate_year9_students
from Generate_year1 import generate_year1_students
from Generate_year2 import generate_year2_students
import random

def generate_year3_students(year2_data):
    """Generate Year 3 data for students who passed Year 2.

    The output list includes only students who passed Year 2 and were not
    expelled, and preserves each student's original ID.
    """

    # Filter: only students who passed Year 2 and weren't expelled
    year2_passed = [s for s in year2_data if s['passed_year2'] and not s['expelled']]

    year3_data = []
    students_for_elimination = []

    comp_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}
    award_counters = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}

    for year2_student in year2_passed:

        student_id = year2_student["id"]

        # Carry personality from Year 2 with a small drift
        student_personality = random.gauss(year2_student["personality"], 0.1)

        # Adjust personality based on Year 2 experience
        if year2_student["ponavljanje"]:
            student_personality += random.gauss(-0.1, 0.15)
        if year2_student["year2_overall"] < 2.5:
            student_personality += random.gauss(-0.08, 0.12)

        # Year 9 data
        grade9 = year2_student["grade9"]
        mat9   = year2_student["mat9"]
        slo9   = year2_student["slo9"]
        ang9   = year2_student["ang9"]

        # Carried-forward data
        year1_overall = year2_student["year1_overall"]
        year2_overall = year2_student["year2_overall"]
        mat2 = year2_student["mat2"]
        slo2 = year2_student["slo2"]
        ang2 = year2_student["ang2"]

        # Weight formula: 80/20 blend so full history is carried forward
        #   weight_y1 = (year1_overall * 0.9) + (grade9 * 0.1)
        #   weight_y2 = (year2_overall * 0.80) + (weight_y1 * 0.20)
        weight_y1 = (year1_overall * 0.9) + (grade9 * 0.1)
        weight_y2 = (year2_overall * 0.80) + (weight_y1 * 0.20)

        # Year 3 grades: same 5-assessment loop as Year 2
        subjects_order = [('mat', mat2), ('slo', slo2), ('ang', ang2)]
        random.shuffle(subjects_order)
        grade3_results = {}
        grade1_count = 0
        any_had_grade1 = False

        for subj_name, subj2 in subjects_order:
            boost = grade1_count * 0.35
            assessments = []
            subj_had_grade1 = False
            for _ in range(5):
                g = grades3(
                    subj2, weight_y2, student_personality,
                    up_shift=(0.05, 0.22), down_shift=(-0.62, 0.30),
                    motivation_boost=boost
                )
                assessments.append(g)
                if g == 1:
                    subj_had_grade1 = True
            grade3_results[subj_name] = min(5, max(1, round(sum(assessments) / 5)))
            if subj_had_grade1:
                any_had_grade1 = True
                grade1_count += 1

        mat3 = grade3_results['mat']
        slo3 = grade3_results['slo']
        ang3 = grade3_results['ang']
        base3 = (mat3 + slo3 + ang3) / 3

        base = ((year2_overall * 0.88) + (grade9 * 0.12)) * 0.25 + (base3 * 0.75)

        num_of_comp, list_competitions, list_competitions_nat = competitions(base, comp_counters)
        num_of_awards = awards(base, num_of_comp, list_competitions, list_competitions_nat, award_counters)

        experience_bonus = ((len(list_competitions) - len(list_competitions_nat)) * 0.15) + (len(list_competitions_nat) * 0.25)
        experience_bonus = min(experience_bonus, 5)
        skupno = (base * 0.9) + (experience_bonus * 0.1)

        year3_student = {
            'id': student_id,
            'grade9': grade9,
            'mat9': mat9,
            'slo9': slo9,
            'ang9': ang9,
            'year1_overall': year1_overall,
            'year2_overall': year2_overall,
            'mat1': year2_student['mat1'],
            'slo1': year2_student['slo1'],
            'ang1': year2_student['ang1'],
            'mat2': mat2,
            'slo2': slo2,
            'ang2': ang2,
            'mat3': mat3,
            'slo3': slo3,
            'ang3': ang3,
            'base': base,
            'any_had_grade1': any_had_grade1,
            'num_of_comp': num_of_comp,
            'num_of_awards': num_of_awards,
            'list_competitions': list_competitions,
            'list_competitions_nat': list_competitions_nat,
        }

        year3_data.append(year3_student)
        students_for_elimination.append({
            'id': student_id,
            'skupno': skupno,
            'list_competitions_nat': list_competitions_nat,
            'awards_list': num_of_awards
        })

    qualified_dict = eliminate_students(students_for_elimination)

    for student in year3_data:
        student['qualified_nationals'] = qualified_dict.get(student['id'], [])
        student['num_of_national_comp'] = len(student['qualified_nationals'])

        student['national_awards_list'] = national_awards(student['base'], student['qualified_nationals'])
        student['num_of_national_awards'] = len(student['national_awards_list'])

        num_awards = len(student['num_of_awards'])

        personality = student_personality
        student['personality'] = round(personality, 3)

        student['num_of_hours_late_for_class'] = late_for_class(
            student['base'], student['num_of_comp'], num_awards,
            student['num_of_national_comp'], student['num_of_national_awards'], personality
        )
        student['num_of_hours_student_was_sent_out'] = hours_sent_out(
            student['base'], student['num_of_comp'], num_awards,
            student['num_of_national_comp'], student['num_of_national_awards'],
            student['num_of_hours_late_for_class'], personality
        )
        student['num_of_intentionally_missed_hours'] = intentionally_missed_hours(
            student['base'], student['num_of_comp'], num_awards,
            student['num_of_national_comp'], student['num_of_national_awards'], personality
        )
        student['all_missed_hours'] = all_missed(
            student['num_of_hours_late_for_class'],
            student['num_of_hours_student_was_sent_out'],
            student['num_of_intentionally_missed_hours']
        )

        sub_base = (student['grade9'] + student['mat9'] + student['slo9'] + student['ang9']) / 4
        weight_for_unexcused = (student['base'] * 0.85) + (sub_base * 0.15) + personality

        student['unexcused_hours_lfc'] = unexcused_hours(
            student['num_of_hours_late_for_class'], weight_for_unexcused, unexcused_late_rates)
        student['unexcused_hours_sso'] = unexcused_hours(
            student['num_of_hours_student_was_sent_out'], weight_for_unexcused, unexcused_sent_out_rates)
        student['unexcused_hours_imh'] = unexcused_hours(
            student['num_of_intentionally_missed_hours'], weight_for_unexcused, unexcused_missed_rates)

        student['all_unexcused_hours'] = (
            student['unexcused_hours_lfc'] +
            student['unexcused_hours_sso'] +
            student['unexcused_hours_imh']
        )

        student['num_of_VU'], student['expelled'] = ukori(student['all_unexcused_hours'])

        if naredil(student) and not student.get('any_had_grade1', False):
            student['ponavljanje'] = False
            student['passed_year3'] = True
        else:
            student['ponavljanje'] = True
            passed, updated_grades = ponavljanje(student, student['base'])
            student['passed_year3'] = passed
            student['mat3'] = updated_grades['mat3']
            student['slo3'] = updated_grades['slo3']
            student['ang3'] = updated_grades['ang3']

        student['grade3'] = student['passed_year3']
        student['year3_overall'] = year3_overall(student)

    return year3_data


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

failure_probs = [
    (2.0, 0.017), (2.3, 0.012), (2.6, 0.008), (3.0, 0.004),
    (3.5, 0.002), (4.0, 0.001), (float("inf"), 0.0003)
]

good_outcome_probs = [
    (1.8, 0.05), (2.0, 0.15), (2.3, 0.28), (2.5, 0.48),
    (2.8, 0.68), (3.0, 0.80), (3.3, 0.87), (3.5, 0.92),
    (3.8, 0.95), (4.0, 0.97), (float("inf"), 0.99)
]

def grades3(subject2, weight_year2, student_personality,
            up_shift=(0.05, 0.22), down_shift=(-0.20, 0.20),
            vlo_down_shift=(-0.15, 0.12), motivation_boost=0.0, ponavljanje=False):
    """Generate a single Year 3 assessment grade."""
    base = (subject2 * 0.3) + (weight_year2 * 0.7) + motivation_boost

    if ponavljanje:
        shift = random.gauss(-0.35, 0.30)
    else:
        good_chance = 0.50
        for limit, probability in good_outcome_probs:
            if base <= limit:
                good_chance = probability
                break

        fail_chance = 0.0
        for limit, prob in failure_probs:
            if base <= limit:
                fail_chance = prob
                break
        if random.random() < fail_chance:
            return 1

        if random.random() < good_chance:
            shift = random.gauss(up_shift[0], up_shift[1])
        elif base < 2.3:
            shift = random.gauss(vlo_down_shift[0], vlo_down_shift[1])
        else:
            shift = random.gauss(down_shift[0], down_shift[1])

    return min(5, max(1, round(base + shift + student_personality * 0.25)))


weight_probs = [
    (1.8, 0.001), (2.0, 0.003), (2.3, 0.005), (2.5, 0.008),
    (2.8, 0.010), (3.0, 0.015), (3.3, 0.020), (3.5, 0.030),
    (3.8, 0.050), (4.0, 0.085), (4.2, 0.115), (4.4, 0.150),
    (4.5, 0.200), (4.7, 0.300), (4.85, 0.600),(float("inf"), 0.750)
]

def competitions(base, comp_counters):
    list_competitions = []
    list_competitions_nat = []
    competitions_with_nationals = {1, 2, 4, 6, 7, 9, 10}
    for i in range(1, 11):
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
    (1.8, 0.003), (2.0, 0.008), (2.3, 0.015), (2.5, 0.030),
    (2.8, 0.060), (3.0, 0.085), (3.3, 0.120), (3.5, 0.170),
    (3.8, 0.240), (4.0, 0.310), (4.2, 0.400), (4.4, 0.500),
    (4.5, 0.620), (4.7, 0.700), (4.85, 0.750),(float("inf"), 0.850)
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
    comp_total_participants = {1: 0, 2: 0, 4: 0, 6: 0, 7: 0, 9: 0, 10: 0}
    comp_award_winners      = {1: [], 2: [], 4: [], 6: [], 7: [], 9: [], 10: []}
    for student in all_students_data:
        for comp_id_str in student['list_competitions_nat']:
            comp_id = int(comp_id_str)
            if comp_id in [1, 2, 4, 6, 7, 9, 10]:
                comp_total_participants[comp_id] += 1
    for student in all_students_data:
        skupno = student['skupno']
        for award_comp_id_str in student.get('awards_list', []):
            comp_id = int(award_comp_id_str)
            if comp_id in [1, 2, 4, 6, 7, 9, 10]:
                comp_award_winners[comp_id].append((student['id'], skupno))
    qualified_for_nationals = {}
    for comp_id in [1, 2, 4, 6, 7, 9, 10]:
        award_winners = comp_award_winners[comp_id]
        if not award_winners:
            continue
        capacity = max(1, int(comp_total_participants[comp_id] * 0.25))
        award_winners.sort(key=lambda x: x[1], reverse=True)
        for i in range(min(len(award_winners), capacity)):
            sid = award_winners[i][0]
            if sid not in qualified_for_nationals:
                qualified_for_nationals[sid] = []
            qualified_for_nationals[sid].append(comp_id)
    return qualified_for_nationals


national_award_probs = [
    (1.8, 0.0003),(2.0, 0.0005),(2.3, 0.001),(2.5, 0.002),
    (2.8, 0.004), (3.0, 0.006), (3.3, 0.010),(3.5, 0.015),
    (3.8, 0.025), (4.0, 0.040), (4.2, 0.060),(4.4, 0.090),
    (4.5, 0.180), (4.7, 0.220), (4.85, 0.280),(float("inf"), 0.350)
]

def national_awards(base, qualified_nationals):
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


late_probs = [
    (1.0, 0.070),(1.3, 0.050),(1.5, 0.035),(1.8, 0.020),
    (2.0, 0.012),(2.3, 0.005),(2.5, 0.003),(2.8, 0.0015),
    (3.0, 0.0008),(3.3, 0.0004),(3.5, 0.0002),(3.8, 0.0001),
    (4.0, 0.00005),(4.5, 0.00002),(float("inf"), 0.000005)
]

def late_for_class(base, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_late_class = 0
    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight = (base * 0.75) + ((base_reg * 0.20 + base_nat * 0.80) * 0.25) + personality
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


sent_out_probs = [
    (1.0, 0.008),(1.3, 0.005),(1.5, 0.003),(1.8, 0.0015),
    (2.0, 0.0008),(2.3, 0.0003),(2.5, 0.00015),(2.8, 0.00006),
    (3.0, 0.00002),(3.5, 0.000005),(float("inf"), 0.000001)
]

lateness_multipliers = [
    (15, 1.0),(25, 1.1),(40, 1.3),(60, 1.5),(float("inf"), 1.8)
]

def hours_sent_out(base, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, num_late_class, personality=0):
    num_sent_out = 0
    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight = (base * 0.75) + ((base_reg * 0.20 + base_nat * 0.80) * 0.25) + personality
    lateness_multiplier = 1.8
    for limit, multiplier in lateness_multipliers:
        if num_late_class < limit:
            lateness_multiplier = multiplier
            break
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


skip_probs = [
    (1.0, 0.14),(1.3, 0.09),(1.5, 0.06),(1.8, 0.038),
    (2.0, 0.025),(2.3, 0.018),(2.5, 0.013),(2.8, 0.009),
    (3.0, 0.006),(3.3, 0.003),(3.5, 0.0015),(3.8, 0.0007),
    (4.0, 0.0003),(4.5, 0.0001),(float("inf"), 0.00003)
]

def intentionally_missed_hours(base, num_of_comp, num_of_awards, num_of_national_comp, num_of_national_awards, personality=0):
    num_missed = 0
    base_reg = (num_of_comp * 0.25) + (num_of_awards * 0.75)
    base_nat = (num_of_national_comp * 0.25) + (num_of_national_awards * 0.75)
    weight = (base * 0.75) + ((base_reg * 0.20 + base_nat * 0.80) * 0.25) + personality
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


def all_missed(lfc, sso, imh):
    return lfc + sso + imh


unexcused_late_rates = [
    (1.8, 0.04),(2.0, 0.035),(2.3, 0.03),(2.5, 0.025),
    (2.8, 0.02),(3.0, 0.018),(3.3, 0.015),(3.5, 0.013),
    (3.8, 0.011),(4.0, 0.010),(4.2, 0.008),(4.5, 0.006),
    (4.7, 0.005),(5.0, 0.004),(float("inf"), 0.003)
]
unexcused_sent_out_rates = [(float("inf"), 1.0)]
unexcused_missed_rates = [
    (1.8, 0.03),(2.0, 0.025),(2.5, 0.02),(3.0, 0.015),
    (3.5, 0.01),(4.0, 0.007),(float("inf"), 0.005)
]

def unexcused_hours(total_hours, weight, rate_table):
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
    num_of_VU = int(all_unexcused_hours // 10)
    expelled = num_of_VU >= 4
    return num_of_VU, expelled


def year3_overall(student):
    """Calculate the overall Year 3 score (1-5 scale)."""
    grade_avg = (student['mat3'] + student['slo3'] + student['ang3']) / 3
    extra = 3.0
    extra += student['num_of_comp'] * 0.2
    extra += len(student['num_of_awards']) * 0.3
    extra += student.get('num_of_national_comp', 0) * 0.3
    extra += student.get('num_of_national_awards', 0) * 0.5
    extra -= student.get('all_unexcused_hours', 0) * 0.05
    extra -= student.get('num_of_VU', 0) * 0.5
    extra = min(5.0, max(1.0, extra))
    return round((grade_avg * 0.9) + (extra * 0.1), 2)


def ponavljanje(student, base):
    """Handle retaking for Year 3 students."""
    subjects = {'mat3': student['mat3'], 'slo3': student['slo3'], 'ang3': student['ang3']}
    failed_subjects = [sub for sub, grade in subjects.items() if grade == 1]
    if len(failed_subjects) == 0:
        return True, subjects
    if len(failed_subjects) == 3:
        return False, subjects
    pass_chance = min(0.95, max(0.75, (base - 1) * 0.10 + 0.65))
    updated = dict(subjects)
    for sub in failed_subjects:
        passed_retake = False
        for attempt in range(2):
            if random.random() < pass_chance:
                passed_retake = True
                updated[sub] = 2
                break
        if not passed_retake:
            return False, updated
    return True, updated


def naredil(student):
    """Check if a student passed Year 3 directly (all grades >= 2)."""
    return student['mat3'] >= 2 and student['slo3'] >= 2 and student['ang3'] >= 2
