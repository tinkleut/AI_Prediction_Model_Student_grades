import csv
import os
import sys
import random
from collections import defaultdict
from Generate_year9 import generate_year9_students
from Generate_year1 import generate_year1_students, competitions, awards

# Ensure Unicode output works in Windows consoles with legacy encodings
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# No fixed seed: each run generates a unique cohort of students
year9_students = generate_year9_students(id_student=0, num_student=10000)
year1_students = generate_year1_students(year9_students)

print('='*80)
print('COMPLETE DATA OVERVIEW - 10,000 STUDENTS')
print('='*80)
print()

# Quick summary stats
nationals_count = sum(1 for s in year1_students if len(s.get('qualified_nationals', [])) > 0)
nat_awards_count = sum(1 for s in year1_students if len(s.get('national_awards_list', [])) > 0)
print(f'Quick Stats:')
print(f'  Students who qualified for nationals: {nationals_count:5} ({nationals_count/len(year1_students)*100:.1f}%)')
print(f'  Students who won national awards:     {nat_awards_count:5} ({nat_awards_count/len(year1_students)*100:.1f}%)')
print()

# Grade 9 overall grade distribution
print('GRADE 9 OVERALL DISTRIBUTION')
print('-'*80)
grade9_dist = {2: 0, 3: 0, 4: 0, 5: 0}
for s in year9_students:
    grade = round(s['grade9'])
    if grade in grade9_dist:
        grade9_dist[grade] += 1

total = sum(grade9_dist.values())
for grade in sorted(grade9_dist.keys()):
    count = grade9_dist[grade]
    pct = count / total * 100
    bar = '█' * int(pct / 2)
    print(f'  Grade {grade}: {count:5} students ({pct:5.1f}%) {bar}')
print()

# Subject distributions (Year 9)
print('YEAR 9 SUBJECT DISTRIBUTIONS')
print('-'*80)
for subject in ['mat9', 'slo9', 'ang9']:
    subject_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_sum = 0
    count_students = 0
    for s in year9_students:
        grade = round(s[subject])
        if grade in subject_dist:
            subject_dist[grade] += 1
        total_sum += s[subject]
        count_students += 1
    
    avg = total_sum / count_students
    print(f'{subject.upper()}:')
    for grade in sorted(subject_dist.keys()):
        count = subject_dist[grade]
        pct = count / count_students * 100
        bar = '█' * int(pct / 2)
        print(f'  Grade {grade}: {count:5} students ({pct:5.1f}%) {bar}')
    print(f'  Average: {avg:.2f}')
    print()

# Year 1 subject distributions
print('YEAR 1 SUBJECT DISTRIBUTIONS')
print('-'*80)

# Calculate overall Year 1 average first
total_year1_sum = 0
for s in year1_students:
    year1_avg = (s['mat1'] + s['slo1'] + s['ang1']) / 3
    total_year1_sum += year1_avg
overall_year1_avg = total_year1_sum / len(year1_students)

print(f'OVERALL YEAR 1 AVERAGE: {overall_year1_avg:.2f}')
print()

for subject_name, year1_subject in [('MAT1', 'mat1'), ('SLO1', 'slo1'), ('ANG1', 'ang1')]:
    subject_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_sum = 0
    count_students = 0
    for s in year1_students:
        grade = round(s[year1_subject])
        if grade in subject_dist:
            subject_dist[grade] += 1
        total_sum += s[year1_subject]
        count_students += 1
    
    avg = total_sum / count_students
    print(f'{subject_name}:')
    for grade in sorted(subject_dist.keys()):
        count = subject_dist[grade]
        pct = count / count_students * 100
        bar = '█' * int(pct / 2)
        print(f'  Grade {grade}: {count:5} students ({pct:5.1f}%) {bar}')
    print(f'  Average: {avg:.2f}')
    print()

# Competitions distribution
print('COMPETITIONS DISTRIBUTION (Year 1)')
print('-'*80)
comp_dist = {}
total_comps = 0
for s in year1_students:
    grade9 = s['grade9']
    mat9, slo9, ang9 = s['mat9'], s['slo9'], s['ang9']
    mat1, slo1, ang1 = s['mat1'], s['slo1'], s['ang1']
    
    num_comp, _, _ = competitions(grade9, mat1, ang1, slo1, mat9, slo9, ang9, defaultdict(int))
    if num_comp not in comp_dist:
        comp_dist[num_comp] = 0
    comp_dist[num_comp] += 1
    total_comps += num_comp

for comp_count in sorted(comp_dist.keys()):
    count = comp_dist[comp_count]
    pct = count / 10000 * 100
    bar = '█' * int(pct / 2)
    print(f'  {comp_count:2} comps: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_comps / 10000:.2f} competitions per student')
print()

# Awards distribution
print('AWARDS DISTRIBUTION (Year 1)')
print('-'*80)
awards_dist = {}
total_awards = 0
perfect_records = 0
students_with_comps = 0
for s in year1_students:
    grade9 = s['grade9']
    mat9, slo9, ang9 = s['mat9'], s['slo9'], s['ang9']
    mat1, slo1, ang1 = s['mat1'], s['slo1'], s['ang1']
    
    num_comp, list_competitions, list_competitions_nat = competitions(grade9, mat1, ang1, slo1, mat9, slo9, ang9, defaultdict(int))
    awards_result = awards(grade9, mat1, slo1, ang1, mat9, slo9, ang9, num_comp, list_competitions, list_competitions_nat, defaultdict(int))
    # Handle both int (0) and list return types
    num_awards = awards_result if isinstance(awards_result, int) else len(awards_result)
    
    # Only count students who attended competitions
    if num_comp > 0:
        students_with_comps += 1
        if num_awards not in awards_dist:
            awards_dist[num_awards] = 0
        awards_dist[num_awards] += 1
        total_awards += num_awards
        
        if num_awards == num_comp:
            perfect_records += 1

print(f'Note: Showing only students who attended competitions (n={students_with_comps})')
print()
for award_count in sorted(awards_dist.keys()):
    count = awards_dist[award_count]
    pct = count / students_with_comps * 100 if students_with_comps > 0 else 0
    bar = '█' * int(pct / 2)
    print(f'  {award_count:2} awards: {count:5} students ({pct:5.1f}%) {bar}')
if students_with_comps > 0:
    print(f'  Average: {total_awards / students_with_comps:.2f} awards per student (who competed)')
    print(f'  Perfect records (awards=comps): {perfect_records} students ({perfect_records/students_with_comps*100:.1f}% of competitors)')
print()

# National competitions distribution
print('NATIONAL COMPETITIONS DISTRIBUTION (Year 1)')
print('-'*80)
nat_comp_dist = {}
total_nat_comps = 0
for s in year1_students:
    qualified = s.get('qualified_nationals', [])
    num_nat_comp = len(qualified)
    if num_nat_comp not in nat_comp_dist:
        nat_comp_dist[num_nat_comp] = 0
    nat_comp_dist[num_nat_comp] += 1
    total_nat_comps += num_nat_comp

for nat_count in sorted(nat_comp_dist.keys()):
    count = nat_comp_dist[nat_count]
    pct = count / 10000 * 100
    bar = '█' * int(pct / 2)
    print(f'  {nat_count:2} nationals: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_nat_comps / 10000:.2f} national competitions per student')
print()

# National awards distribution
print('NATIONAL AWARDS DISTRIBUTION (Year 1)')
print('-'*80)
nat_awards_dist = {}
total_nat_awards = 0
students_at_nationals = sum(1 for s in year1_students if len(s.get('qualified_nationals', [])) > 0)

for s in year1_students:
    qualified = s.get('qualified_nationals', [])
    if len(qualified) > 0:  # Only count students who attended nationals
        nat_awards = s.get('national_awards_list', [])
        num_nat_awards = len(nat_awards) if isinstance(nat_awards, list) else 0
        
        if num_nat_awards not in nat_awards_dist:
            nat_awards_dist[num_nat_awards] = 0
        nat_awards_dist[num_nat_awards] += 1
        total_nat_awards += num_nat_awards

print(f'Note: Showing only students who attended nationals (n={students_at_nationals})')
print()
for nat_award_count in sorted(nat_awards_dist.keys()):
    count = nat_awards_dist[nat_award_count]
    pct = count / students_at_nationals * 100 if students_at_nationals > 0 else 0
    bar = '█' * int(pct / 2)
    print(f'  {nat_award_count:2} nat awards: {count:5} students ({pct:5.1f}%) {bar}')
if students_at_nationals > 0:
    print(f'  Average: {total_nat_awards / students_at_nationals:.2f} national awards per student (who attended nationals)')
print()

# Late for class distribution (using pre-computed data)
print('HOURS LATE FOR CLASS DISTRIBUTION (Year 1)')
print('-'*80)
late_dist = {}
total_late = 0
num_students = len(year1_students)

for s in year1_students:
    hours_late = s.get('num_of_hours_late_for_class', 0)
    total_late += hours_late
    
    if hours_late <= 10:
        range_key = '0-10'
    elif hours_late <= 20:
        range_key = '11-20'
    elif hours_late <= 35:
        range_key = '21-35'
    elif hours_late <= 50:
        range_key = '36-50'
    elif hours_late <= 70:
        range_key = '51-70'
    elif hours_late <= 100:
        range_key = '71-100'
    else:
        range_key = '101+'
    
    if range_key not in late_dist:
        late_dist[range_key] = 0
    late_dist[range_key] += 1

for range_key in ['0-10', '11-20', '21-35', '36-50', '51-70', '71-100', '101+']:
    count = late_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_late / num_students:.2f} hours late per student')
print()

# Hours sent out distribution (using pre-computed data)
print('HOURS SENT OUT OF CLASS DISTRIBUTION (Year 1)')
print('-'*80)
sent_out_dist = {}
total_sent_out = 0

for s in year1_students:
    hours_so = s.get('num_of_hours_student_was_sent_out', 0)
    total_sent_out += hours_so
    
    if hours_so == 0:
        range_key = '0'
    elif hours_so <= 2:
        range_key = '1-2'
    elif hours_so <= 5:
        range_key = '3-5'
    elif hours_so <= 10:
        range_key = '6-10'
    elif hours_so <= 15:
        range_key = '11-15'
    elif hours_so <= 20:
        range_key = '16-20'
    else:
        range_key = '21+'
    
    if range_key not in sent_out_dist:
        sent_out_dist[range_key] = 0
    sent_out_dist[range_key] += 1

for range_key in ['0', '1-2', '3-5', '6-10', '11-15', '16-20', '21+']:
    count = sent_out_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_sent_out / num_students:.2f} hours sent out per student')
print()

# Intentionally missed hours distribution (using pre-computed data)
print('INTENTIONALLY MISSED HOURS DISTRIBUTION (Year 1)')
print('-'*80)
missed_dist = {}
total_missed = 0

for s in year1_students:
    hours_missed = s.get('num_of_intentionally_missed_hours', 0)
    total_missed += hours_missed
    
    if hours_missed <= 5:
        range_key = '0-5'
    elif hours_missed <= 10:
        range_key = '6-10'
    elif hours_missed <= 20:
        range_key = '11-20'
    elif hours_missed <= 30:
        range_key = '21-30'
    elif hours_missed <= 50:
        range_key = '31-50'
    elif hours_missed <= 70:
        range_key = '51-70'
    elif hours_missed <= 100:
        range_key = '71-100'
    elif hours_missed <= 125:
        range_key = '101-125'
    elif hours_missed <= 150:
        range_key = '126-150'
    else:
        range_key = '151+'
    
    if range_key not in missed_dist:
        missed_dist[range_key] = 0
    missed_dist[range_key] += 1

for range_key in ['0-5', '6-10', '11-20', '21-30', '31-50', '51-70', '71-100', '101-125', '126-150', '151+']:
    count = missed_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_missed / num_students:.2f} hours intentionally missed per student')
print()

# All missed hours distribution (using pre-computed data)
print('ALL MISSED HOURS DISTRIBUTION (Year 1)')
print('-'*80)
all_missed_dist = {}
total_all_missed = 0

for s in year1_students:
    all_hours = s.get('all_missed_hours', 0)
    total_all_missed += all_hours
    
    if all_hours <= 20:
        range_key = '0-20'
    elif all_hours <= 50:
        range_key = '21-50'
    elif all_hours <= 100:
        range_key = '51-100'
    elif all_hours <= 150:
        range_key = '101-150'
    elif all_hours <= 200:
        range_key = '151-200'
    else:
        range_key = '201+'
    
    if range_key not in all_missed_dist:
        all_missed_dist[range_key] = 0
    all_missed_dist[range_key] += 1
    
for range_key in ['0-20', '21-50', '51-100', '101-150', '151-200', '201+']:
    count = all_missed_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_all_missed / num_students:.2f} total hours missed per student')
print()

# Unexcused hours: late for class (using pre-computed data)
print('UNEXCUSED HOURS - LATE FOR CLASS (Year 1)')
print('-'*80)
unexc_late_dist = {}
total_unexc_late = 0

for s in year1_students:
    hrs = s.get('unexcused_hours_lfc', 0)
    total_unexc_late += hrs
    
    if hrs == 0:
        range_key = '0'
    elif hrs <= 5:
        range_key = '1-5'
    elif hrs <= 10:
        range_key = '6-10'
    elif hrs <= 20:
        range_key = '11-20'
    elif hrs <= 30:
        range_key = '21-30'
    else:
        range_key = '31+'
    
    if range_key not in unexc_late_dist:
        unexc_late_dist[range_key] = 0
    unexc_late_dist[range_key] += 1

for range_key in ['0', '1-5', '6-10', '11-20', '21-30', '31+']:
    count = unexc_late_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_unexc_late / num_students:.2f} unexcused late hours per student')
print()

# Unexcused hours: sent out of class (using pre-computed data)
print('UNEXCUSED HOURS - SENT OUT OF CLASS (Year 1)')
print('-'*80)

unexc_so_dist = {k: 0 for k in ['0', '1-2', '3-5', '6-10', '11-15', '16-20', '21+']}
total_unexc_so = 0
num_students = len(year1_students)

# 1. Process data and populate the dictionary
for s in year1_students:
    hrs = s.get('unexcused_hours_sso', 0)
    total_unexc_so += hrs
    
    if hrs == 0:
        range_key = '0'
    elif hrs <= 2:
        range_key = '1-2'
    elif hrs <= 5:
        range_key = '3-5'
    elif hrs <= 10:
        range_key = '6-10'
    elif hrs <= 15:
        range_key = '11-15'
    elif hrs <= 20:
        range_key = '16-20'
    else:
        range_key = '21+'
    
    unexc_so_dist[range_key] += 1

# 2. Print the results
for range_key in ['0', '1-2', '3-5', '6-10', '11-15', '16-20', '21+']:
    count = unexc_so_dist[range_key]
    # Guard against division by zero if list is empty
    pct = (count / num_students * 100) if num_students > 0 else 0
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')

avg = total_unexc_so / num_students if num_students > 0 else 0
print(f'\n  Average: {avg:.2f} unexcused sent out hours per student')
print()

# Unexcused hours: intentionally missed (using pre-computed data)
print('UNEXCUSED HOURS - INTENTIONALLY MISSED (Year 1)')
print('-'*80)
unexc_missed_dist = {}
total_unexc_missed = 0

for s in year1_students:
    hrs = s.get('unexcused_hours_imh', 0)
    total_unexc_missed += hrs
    
    if hrs == 0:
        range_key = '0'
    elif hrs <= 3:
        range_key = '1-3'
    elif hrs <= 5:
        range_key = '4-5'
    elif hrs <= 10:
        range_key = '6-10'
    elif hrs <= 15:
        range_key = '11-15'
    elif hrs <= 20:
        range_key = '16-20'
    elif hrs <= 30:
        range_key = '21-30'
    elif hrs <= 40:
        range_key = '31-40'
    else:
        range_key = '41+'
    
    if range_key not in unexc_missed_dist:
        unexc_missed_dist[range_key] = 0
    unexc_missed_dist[range_key] += 1

for range_key in ['0', '1-3', '4-5', '6-10', '11-15', '16-20', '21-30', '31-40', '41+']:
    count = unexc_missed_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_unexc_missed / num_students:.2f} unexcused missed hours per student')
print()

# All unexcused hours combined (using pre-computed data)
print('ALL UNEXCUSED HOURS COMBINED (Year 1)')
print('-'*80)
all_unexc_dist = {}
total_all_unexc = 0

for s in year1_students:
    hrs = s.get('all_unexcused_hours', 0)
    total_all_unexc += hrs
    
    if hrs <= 1:
        range_key = '0'
    elif hrs <= 3:
        range_key = '1-3'
    elif hrs <= 5:
        range_key = '4-5'
    elif hrs <= 10:
        range_key = '6-10'
    elif hrs <= 15:
        range_key = '11-15'
    elif hrs <= 20:
        range_key = '16-20'
    elif hrs <= 25:
        range_key = '21-25'
    elif hrs <= 30:
        range_key = '26-30'
    elif hrs <= 35:
        range_key = '31-35'
    elif hrs <= 40:
        range_key = '36-39'
    else:
        range_key = '40+'
    
    if range_key not in all_unexc_dist:
        all_unexc_dist[range_key] = 0
    all_unexc_dist[range_key] += 1

for range_key in ['0', '1-3', '4-5', '6-10', '11-15', '16-20', '21-25', '26-30', '31-35', '36-39', '40+']:
    count = all_unexc_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_all_unexc / num_students:.2f} total unexcused hours per student')
print()

# Ukori (disciplinary warnings) distribution (using pre-computed data)
print('DISCIPLINARY WARNINGS (UKORI) DISTRIBUTION (Year 1)')
print('-'*80)
vu_dist = {}
total_vu = 0
expelled_count = 0

for s in year1_students:
    vu = s.get('num_of_VU', 0)
    total_vu += vu
    if s.get('expelled', False):
        expelled_count += 1
    
    if vu not in vu_dist:
        vu_dist[vu] = 0
    vu_dist[vu] += 1

for vu_count in sorted(vu_dist.keys()):
    count = vu_dist[vu_count]
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    label = f'{vu_count} VU'
    if vu_count >= 4:
        label += ' (expelled)'
    print(f'  {label:>15}: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_vu / num_students:.2f} ukori per student')
print(f'  Expelled (4+ VU): {expelled_count} students ({expelled_count / num_students * 100:.2f}%)')
print()

# Year 1 overall score distribution
print('YEAR 1 OVERALL SCORE DISTRIBUTION')
print('-'*80)
overall_dist = {}
total_overall = 0

for s in year1_students:
    score = s.get('year1_overall', 0)
    total_overall += score
    
    if score < 1.5:
        range_key = '<1.5'
    elif score < 2.0:
        range_key = '1.5-2.0'
    elif score < 2.5:
        range_key = '2.0-2.5'
    elif score < 3.0:
        range_key = '2.5-3.0'
    elif score < 3.5:
        range_key = '3.0-3.5'
    elif score < 4.0:
        range_key = '3.5-4.0'
    elif score < 4.5:
        range_key = '4.0-4.5'
    else:
        range_key = '4.5-5.0'
    
    if range_key not in overall_dist:
        overall_dist[range_key] = 0
    overall_dist[range_key] += 1

for range_key in ['<1.5', '1.5-2.0', '2.0-2.5', '2.5-3.0', '3.0-3.5', '3.5-4.0', '4.0-4.5', '4.5-5.0']:
    count = overall_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7}: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_overall / num_students:.2f}')
print()

# Ponavljanje (retake) distribution
print('RETAKE (PONAVLJANJE) DISTRIBUTION (Year 1)')
print('-'*80)
needed_retake = sum(1 for s in year1_students if s.get('ponavljanje', False))
passed_directly = sum(1 for s in year1_students if not s.get('ponavljanje', False))
passed_after_retake = sum(1 for s in year1_students if s.get('ponavljanje', False) and s.get('passed_year1', False))
failed_after_retake = sum(1 for s in year1_students if s.get('ponavljanje', False) and not s.get('passed_year1', False))
total_passed = sum(1 for s in year1_students if s.get('passed_year1', False))

print(f'  Passed directly (all >= 2):  {passed_directly:6} students ({passed_directly / num_students * 100:5.1f}%)')
print(f'  Needed retake:               {needed_retake:6} students ({needed_retake / num_students * 100:5.1f}%)')
print(f'    Passed after retake:       {passed_after_retake:6} students ({passed_after_retake / num_students * 100:5.1f}%)')
print(f'    Failed after retake:       {failed_after_retake:6} students ({failed_after_retake / num_students * 100:5.1f}%)')
print(f'  Total passed Year 1:         {total_passed:6} students ({total_passed / num_students * 100:5.1f}%)')
print()

print('='*80)

# ===== EXPORT ALL STUDENTS TO CSV =====
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'students_year1.csv'))
if os.path.exists(csv_path):
    os.remove(csv_path)
csv_columns = [
    'id', 'grade9', 'mat9', 'slo9', 'ang9',
    'mat1', 'slo1', 'ang1',
    'num_of_comp', 'num_of_awards', 'num_of_national_comp', 'num_of_national_awards',
    'all_missed_hours', 'all_unexcused_hours',
    'num_of_VU', 'retake', 'passed_year1', 'year1_overall'
]

from datetime import datetime

try:
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_columns)
        for s in year1_students:
            num_awards = len(s['num_of_awards'])
            writer.writerow([
                s['id'], s['grade9'], s['mat9'], s['slo9'], s['ang9'],
                s['mat1'], s['slo1'], s['ang1'],
                s['num_of_comp'], num_awards,
                s.get('num_of_national_comp', 0), s.get('num_of_national_awards', 0),
                s.get('all_missed_hours', 0),
                s.get('all_unexcused_hours', 0),
                s.get('num_of_VU', 0),
                s.get('ponavljanje', False),
                s.get('passed_year1', True),
                s.get('year1_overall', 0)
            ])
    print(f'\nExported {num_students} students to {csv_path}')
except PermissionError:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fallback_path = csv_path.replace('.csv', f'_{timestamp}.csv')
    try:
        with open(fallback_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_columns)
            for s in year1_students:
                num_awards = len(s['num_of_awards'])
                writer.writerow([
                    s['id'], s['grade9'], s['mat9'], s['slo9'], s['ang9'],
                    s['mat1'], s['slo1'], s['ang1'],
                    s['num_of_comp'], num_awards,
                    s.get('num_of_national_comp', 0), s.get('num_of_national_awards', 0),
                    s.get('all_missed_hours', 0),
                    s.get('all_unexcused_hours', 0),
                    s.get('num_of_VU', 0),
                    s.get('ponavljanje', False),
                    s.get('passed_year1', True),
                    s.get('year1_overall', 0)
                ])
        print(f'\nExported {num_students} students to {fallback_path} (fallback due to lock)')
    except PermissionError:
        print(f"\nERROR: Unable to write CSV to {csv_path} or fallback {fallback_path}. File may be locked.")
