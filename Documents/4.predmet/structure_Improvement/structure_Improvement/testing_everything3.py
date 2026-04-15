import csv
import os
import sys
import random
from collections import defaultdict
from Generate_year9 import generate_year9_students
from Generate_year1 import generate_year1_students
from Generate_year2 import generate_year2_students
from Generate_year3 import generate_year3_students, competitions as competitions3, awards as awards3

# Ensure Unicode output works in Windows consoles with legacy encodings
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# No fixed seed: each run generates a unique cohort of students
year9_students = generate_year9_students(id_student=0, num_student=10000)
year1_students = generate_year1_students(year9_students)
year2_students = generate_year2_students(year1_students)
year3_students = generate_year3_students(year2_students)

num_students = len(year3_students)

print('='*80)
print('COMPLETE DATA OVERVIEW - YEAR 3 STUDENTS')
print('='*80)
print()

# Quick summary stats
nationals_count = sum(1 for s in year3_students if len(s.get('qualified_nationals', [])) > 0)
nat_awards_count = sum(1 for s in year3_students if len(s.get('national_awards_list', [])) > 0)
total_year1 = len(year1_students)
total_passed_year1 = sum(1 for s in year1_students if s.get('passed_year1', False) and not s.get('expelled', False))
print(f'Quick Stats:')
print(f'  Year 1 students total:                {total_year1:5}')
print(f'  Passed Year 1 (entered Year 3):       {total_passed_year1:5} ({total_passed_year1/total_year1*100:.1f}%)')
print(f'  Year 3 students:                      {num_students:5}')
print(f'  Students who qualified for nationals: {nationals_count:5} ({nationals_count/num_students*100:.1f}%)')
print(f'  Students who won national awards:     {nat_awards_count:5} ({nat_awards_count/num_students*100:.1f}%)')
print()

# Year 3 subject distributions
print('YEAR 3 SUBJECT DISTRIBUTIONS')
print('-'*80)

total_year3_sum = 0
for s in year3_students:
    year3_avg = (s['mat3'] + s['slo3'] + s['ang3']) / 3
    total_year3_sum += year3_avg
overall_year3_avg = total_year3_sum / num_students

print(f'OVERALL YEAR 3 AVERAGE: {overall_year3_avg:.2f}')
print()

for subject_name, year3_subject in [('MAT3', 'mat3'), ('SLO3', 'slo3'), ('ANG3', 'ang3')]:
    subject_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    total_sum = 0
    count_students = 0
    for s in year3_students:
        grade = round(s[year3_subject])
        if grade in subject_dist:
            subject_dist[grade] += 1
        total_sum += s[year3_subject]
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

# Grade 1 breakdown (Year 3)
print('GRADE 1 SUBJECT BREAKDOWN (Year 3)')
print('-'*80)
at_least_one = sum(1 for s in year3_students if s['mat3']==1 or s['slo3']==1 or s['ang3']==1)
exactly_two  = sum(1 for s in year3_students if sum(1 for k in ['mat3','slo3','ang3'] if s[k]==1)==2)
all_three    = sum(1 for s in year3_students if s['mat3']==1 and s['slo3']==1 and s['ang3']==1)
print(f'  At least 1 subject with grade 1: {at_least_one:5} students ({100*at_least_one/num_students:.1f}%)')
print(f'  Exactly 2 subjects with grade 1: {exactly_two:5} students ({100*exactly_two/num_students:.1f}%)')
print(f'  All 3 subjects with grade 1:     {all_three:5} students ({100*all_three/num_students:.1f}%)')
print()

# Competitions distribution (Year 3)
print('COMPETITIONS DISTRIBUTION (Year 3)')
print('-'*80)
comp_dist = {}
total_comps = 0
for s in year3_students:
    num_comp, _, _ = competitions3(s['base'], defaultdict(int))
    if num_comp not in comp_dist:
        comp_dist[num_comp] = 0
    comp_dist[num_comp] += 1
    total_comps += num_comp

for comp_count in sorted(comp_dist.keys()):
    count = comp_dist[comp_count]
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {comp_count:2} comps: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_comps / num_students:.2f} competitions per student')
print()

# Awards distribution (Year 3)
print('AWARDS DISTRIBUTION (Year 3)')
print('-'*80)
awards_dist = {}
total_awards = 0
perfect_records = 0
students_with_comps = 0
for s in year3_students:
    num_comp, list_competitions, list_competitions_nat = competitions3(s['base'], defaultdict(int))
    awards_result = awards3(s['base'], num_comp, list_competitions, list_competitions_nat, defaultdict(int))
    num_awards = awards_result if isinstance(awards_result, int) else len(awards_result)

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

# National competitions distribution (Year 3)
print('NATIONAL COMPETITIONS DISTRIBUTION (Year 3)')
print('-'*80)
nat_comp_dist = {}
total_nat_comps = 0
for s in year3_students:
    qualified = s.get('qualified_nationals', [])
    num_nat_comp = len(qualified)
    if num_nat_comp not in nat_comp_dist:
        nat_comp_dist[num_nat_comp] = 0
    nat_comp_dist[num_nat_comp] += 1
    total_nat_comps += num_nat_comp

for nat_count in sorted(nat_comp_dist.keys()):
    count = nat_comp_dist[nat_count]
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {nat_count:2} nationals: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_nat_comps / num_students:.2f} national competitions per student')
print()

# National awards distribution (Year 3)
print('NATIONAL AWARDS DISTRIBUTION (Year 3)')
print('-'*80)
nat_awards_dist = {}
total_nat_awards = 0
students_at_nationals = sum(1 for s in year3_students if len(s.get('qualified_nationals', [])) > 0)

for s in year3_students:
    qualified = s.get('qualified_nationals', [])
    if len(qualified) > 0:
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

# Late for class distribution (Year 3)
print('HOURS LATE FOR CLASS DISTRIBUTION (Year 3)')
print('-'*80)
late_dist = {}
total_late = 0

for s in year3_students:
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

# Hours sent out distribution (Year 3)
print('HOURS SENT OUT OF CLASS DISTRIBUTION (Year 3)')
print('-'*80)
sent_out_dist = {}
total_sent_out = 0

for s in year3_students:
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

# Intentionally missed hours distribution (Year 3)
print('INTENTIONALLY MISSED HOURS DISTRIBUTION (Year 3)')
print('-'*80)
missed_dist = {}
total_missed = 0

for s in year3_students:
    hours_missed = s.get('num_of_intentionally_missed_hours', 0)
    total_missed += hours_missed

    if hours_missed <= 10:
        range_key = '0-10'
    elif hours_missed <= 30:
        range_key = '11-30'
    elif hours_missed <= 60:
        range_key = '31-60'
    elif hours_missed <= 100:
        range_key = '61-100'
    elif hours_missed <= 150:
        range_key = '101-150'
    else:
        range_key = '151+'

    if range_key not in missed_dist:
        missed_dist[range_key] = 0
    missed_dist[range_key] += 1

for range_key in ['0-10', '11-30', '31-60', '61-100', '101-150', '151+']:
    count = missed_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_missed / num_students:.2f} hours intentionally missed per student')
print()

# All missed hours distribution (Year 3)
print('ALL MISSED HOURS DISTRIBUTION (Year 3)')
print('-'*80)
all_missed_dist = {}
total_all_missed = 0

for s in year3_students:
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

# Unexcused hours: late for class (Year 3)
print('UNEXCUSED HOURS - LATE FOR CLASS (Year 3)')
print('-'*80)
unexc_late_dist = {}
total_unexc_late = 0

for s in year3_students:
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

# Unexcused hours: sent out of class (Year 3)
print('UNEXCUSED HOURS - SENT OUT OF CLASS (Year 3)')
print('-'*80)
unexc_so_dist = {}
total_unexc_so = 0

for s in year3_students:
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
    else:
        range_key = '11+'

    if range_key not in unexc_so_dist:
        unexc_so_dist[range_key] = 0
    unexc_so_dist[range_key] += 1

for range_key in ['0', '1-2', '3-5', '6-10', '11+']:
    count = unexc_so_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_unexc_so / num_students:.2f} unexcused sent out hours per student')
print()

# Unexcused hours: intentionally missed (Year 3)
print('UNEXCUSED HOURS - INTENTIONALLY MISSED (Year 3)')
print('-'*80)
unexc_missed_dist = {}
total_unexc_missed = 0

for s in year3_students:
    hrs = s.get('unexcused_hours_imh', 0)
    total_unexc_missed += hrs

    if hrs == 0:
        range_key = '0'
    elif hrs <= 5:
        range_key = '1-5'
    elif hrs <= 15:
        range_key = '6-15'
    elif hrs <= 30:
        range_key = '16-30'
    elif hrs <= 50:
        range_key = '31-50'
    else:
        range_key = '51+'

    if range_key not in unexc_missed_dist:
        unexc_missed_dist[range_key] = 0
    unexc_missed_dist[range_key] += 1

for range_key in ['0', '1-5', '6-15', '16-30', '31-50', '51+']:
    count = unexc_missed_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_unexc_missed / num_students:.2f} unexcused missed hours per student')
print()

# All unexcused hours combined (Year 3)
print('ALL UNEXCUSED HOURS COMBINED (Year 3)')
print('-'*80)
all_unexc_dist = {}
total_all_unexc = 0

for s in year3_students:
    hrs = s.get('all_unexcused_hours', 0)
    total_all_unexc += hrs

    if hrs <= 5:
        range_key = '0-5'
    elif hrs <= 15:
        range_key = '6-15'
    elif hrs <= 30:
        range_key = '16-30'
    elif hrs <= 50:
        range_key = '31-50'
    elif hrs <= 75:
        range_key = '51-75'
    else:
        range_key = '76+'

    if range_key not in all_unexc_dist:
        all_unexc_dist[range_key] = 0
    all_unexc_dist[range_key] += 1

for range_key in ['0-5', '6-15', '16-30', '31-50', '51-75', '76+']:
    count = all_unexc_dist.get(range_key, 0)
    pct = count / num_students * 100
    bar = '█' * int(pct / 2)
    print(f'  {range_key:>7} hrs: {count:6} students ({pct:5.1f}%) {bar}')
print(f'  Average: {total_all_unexc / num_students:.2f} total unexcused hours per student')
print()

# Ukori (disciplinary warnings) distribution (Year 3)
print('DISCIPLINARY WARNINGS (UKORI) DISTRIBUTION (Year 3)')
print('-'*80)
vu_dist = {}
total_vu = 0
expelled_count = 0

for s in year3_students:
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

# Year 3 overall score distribution
print('YEAR 3 OVERALL SCORE DISTRIBUTION')
print('-'*80)
overall_dist = {}
total_overall = 0

for s in year3_students:
    score = s.get('year3_overall', 0)
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

# Ponavljanje (retake) distribution (Year 3)
print('RETAKE (PONAVLJANJE) DISTRIBUTION (Year 3)')
print('-'*80)
needed_retake = sum(1 for s in year3_students if s.get('ponavljanje', False))
passed_directly = sum(1 for s in year3_students if not s.get('ponavljanje', False))
passed_after_retake = sum(1 for s in year3_students if s.get('ponavljanje', False) and s.get('passed_year3', False))
failed_after_retake = sum(1 for s in year3_students if s.get('ponavljanje', False) and not s.get('passed_year3', False))
total_passed = sum(1 for s in year3_students if s.get('passed_year3', False))

print(f'  Passed directly (all >= 2):  {passed_directly:6} students ({passed_directly / num_students * 100:5.1f}%)')
print(f'  Needed retake:               {needed_retake:6} students ({needed_retake / num_students * 100:5.1f}%)')
print(f'    Passed after retake:       {passed_after_retake:6} students ({passed_after_retake / num_students * 100:5.1f}%)')
print(f'    Failed after retake:       {failed_after_retake:6} students ({failed_after_retake / num_students * 100:5.1f}%)')
print(f'  Total passed Year 3:         {total_passed:6} students ({total_passed / num_students * 100:5.1f}%)')

print()

print('='*80)

# ===== EXPORT ALL STUDENTS TO CSV =====
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'students_year3.csv'))
if os.path.exists(csv_path):
    os.remove(csv_path)
csv_columns = [
    'id', 'grade9', 'mat9', 'slo9', 'ang9',
    'mat1', 'slo1', 'ang1',
    'mat2', 'slo2', 'ang2',
    'mat3', 'slo3', 'ang3',
    'num_of_comp', 'num_of_awards', 'num_of_national_comp', 'num_of_national_awards',
    'all_missed_hours', 'all_unexcused_hours',
    'num_of_VU', 'ponavljanje', 'passed_year3', 'year3_overall'
]

from datetime import datetime

try:
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_columns)
        for s in year3_students:
            num_awards = len(s['num_of_awards'])
            writer.writerow([
                s['id'], s['grade9'], s['mat9'], s['slo9'], s['ang9'],
                s['mat1'], s['slo1'], s['ang1'],
                s['mat2'], s['slo2'], s['ang2'],
                s['mat3'], s['slo3'], s['ang3'],
                s['num_of_comp'], num_awards,
                s.get('num_of_national_comp', 0), s.get('num_of_national_awards', 0),
                s.get('all_missed_hours', 0),
                s.get('all_unexcused_hours', 0),
                s.get('num_of_VU', 0),
                s.get('ponavljanje', False),
                s.get('passed_year3', True),
                s.get('year3_overall', 0)
            ])
    print(f'\nExported {num_students} students to {csv_path}')
except PermissionError:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    fallback_path = csv_path.replace('.csv', f'_{timestamp}.csv')
    try:
        with open(fallback_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_columns)
            for s in year3_students:
                num_awards = len(s['num_of_awards'])
                writer.writerow([
                    s['id'], s['grade9'], s['mat9'], s['slo9'], s['ang9'],
                    s['mat1'], s['slo1'], s['ang1'],
                    s['mat2'], s['slo2'], s['ang2'],
                    s['mat3'], s['slo3'], s['ang3'],
                    s['num_of_comp'], num_awards,
                    s.get('num_of_national_comp', 0), s.get('num_of_national_awards', 0),
                    s.get('all_missed_hours', 0),
                    s.get('all_unexcused_hours', 0),
                    s.get('num_of_VU', 0),
                    s.get('ponavljanje', False),
                    s.get('passed_year3', True),
                    s.get('year3_overall', 0)
                ])
        print(f'\nExported {num_students} students to {fallback_path} (fallback due to lock)')
    except PermissionError:
        print(f"\nERROR: Unable to write CSV to {csv_path} or fallback {fallback_path}. File may be locked.")
