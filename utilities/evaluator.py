
# Input 1: Annotated data with labels '0' and '1'.
# Input 2: Decision log from the output of the TMOP
# Output:  A result file with evaluation measures like Accuracy, Precision, Recall, etc


# Create 4 files for True-Positive, True-negative, etc
write_to_files = True
# Input 1
gold_file_name = 'gold_en_it.csv'
# Input 2
tm_results_file_name = 'decision_log__en_it_with_gold.csv'

output_file_name = "results"


# ------------------------------------------------------------

goldf = open(gold_file_name, 'r')
resf = open(tm_results_file_name, 'r')

if write_to_files:
	tp_file = open("separated/tp", 'w')
	tn_file = open("separated/tn", 'w')
	fp_file = open("separated/fp", 'w')
	fn_file = open("separated/fn", 'w')

tp, tn, fp, fn = 0., 0., 0., 0.
n_acc_tp, n_acc_fp = 0., 0.
n_rej_tn, n_rej_fn = 0., 0.

for gline in goldf:
	rline = resf.readline()

	gline = gline.strip().split('\t')
	rline = rline.strip().split('\t')

	rline = rline[1:]  # remove ID
	rline[0] = int(rline[0])
	gline[3] = int(gline[3])

	if rline[0] == 2 and gline[3] == 1:
		tp += 1
		if write_to_files:
			tp_file.write("\t".join(gline[:3]) + "\n")
	elif rline[0] == 2 and gline[3] == 0:
		fp += 1
		if write_to_files:
			fp_file.write("\t".join(gline[:3]) + "\n")
	elif rline[0] == 0 and gline[3] == 1:
		fn += 1
		if write_to_files:
			fn_file.write("\t".join(gline[:3]) + "\n")
	elif rline[0] == 0 and gline[3] == 0:
		tn += 1
		if write_to_files:
			tn_file.write("\t".join(gline[:3]) + "\n")

	# checking the neutral answer and their statistics
	if rline[0] == 1 and gline[3] == 1:
		n_acc_tp += 1
		n_rej_fn += 1
	elif rline[0] == 1 and gline[3] == 0:
		n_acc_fp += 1
		n_rej_tn += 1

goldf.close()
resf.close()

if write_to_files:
	tp_file.close()
	tn_file.close()
	fp_file.close()
	fn_file.close()

#------------------------------------------------------------------

if (tp + tn + fp + fn) == 0:
	print("No statistics to show.")
	print("All the numbers are zero.")
	exit()

#------------------------------------------------------------------

output_file = open(output_file_name, 'w')

print("True Positive: {}".format(tp))
print("True Negative: {}".format(tn))
print("False Positive: {}".format(fp))
print("False Negative: {}".format(fn))

output_file.write("True Positive: " + str(tp) + "\n")
output_file.write("True Negative: " + str(tn) + "\n")
output_file.write("False Positive: " + str(fp) + "\n")
output_file.write("False Negative: " + str(fn) + "\n")

print("\n----------------------------------\n")
output_file.write("\n----------------------------------\n")

acc = round((tp + tn)/(tp + tn + fp + fn), 3)
bal_acc = round(0.5 * (tp/max(0.1, (tp + fn)) + tn/max(0.1, (tn + fp))), 3)
prec = round(tp / max(0.1, (tp + fp)), 3)
rec = round(tp / max(0.1, (tp + fn)), 3)
f1 = round((2. * tp) / max(0.1, ((2. * tp) + fp + fn)), 3)

print("Accuracy :\t" + str(acc) + "\n")
print("Balanced Acc :\t" + str(bal_acc) + "\n")
print("Precision :\t" + str(prec) + "\n")
print("Recall :\t" + str(rec) + "\n")
print("F1 Measure :\t" + str(f1) + "\n")

output_file.write("Accuracy :\t" + str(acc) + "\n")
output_file.write("Balanced Acc :\t" + str(bal_acc) + "\n")
output_file.write("Precision :\t" + str(prec) + "\n")
output_file.write("Recall :\t" + str(rec) + "\n")
output_file.write("F1 Measure :\t" + str(f1) + "\n")

print("\nWith neutrals as accepted:")
print("--------------------------\n")
output_file.write("\nWith neutrals as accepted:\n")
output_file.write("--------------------------\n\n")

acc = round((tp + n_acc_tp + tn) / (tp + n_acc_tp + tn + fp + n_acc_fp + fn), 3)
prec = round((tp + n_acc_tp) / max(0.1, (tp + n_acc_tp + fp + n_acc_fp)), 3)
rec = round((tp + n_acc_tp) / max(0.1, (tp + n_acc_tp + fn)), 3)
f1 = round((2. * (tp + n_acc_tp)) / max(0.1, (2. * (tp + n_acc_tp) + fp + n_acc_fp + fn)), 3)

print("Accuracy :\t" + str(acc) + "\n")
print("Precision :\t" + str(prec) + "\n")
print("Recall :\t" + str(rec) + "\n")
print("F1 Measure :\t" + str(f1) + "\n")

output_file.write("Accuracy :\t" + str(acc) + "\n")
output_file.write("Precision :\t" + str(prec) + "\n")
output_file.write("Recall :\t" + str(rec) + "\n")
output_file.write("F1 Measure :\t" + str(f1) + "\n")

print("\nWith neutrals as rejected:")
print("--------------------------\n")
output_file.write("\nWith neutrals as rejected:\n")
output_file.write("--------------------------\n\n")

acc = round((tp + tn + n_rej_tn) / max(0.1, (tp + tn + n_rej_tn + fp + fn + n_rej_fn)), 3)
prec = round(tp / max(0.1, (tp + fp)), 3)
rec = round(tp / max((tp + fn + n_rej_fn)), 3)
f1 = round((2. * tp) / max(((2. * tp) + fp + fn + n_rej_fn)), 3)

print("Accuracy :\t" + str(acc) + "\n")
print("Precision :\t" + str(prec) + "\n")
print("Recall :\t" + str(rec) + "\n")
print("F1 Measure :\t" + str(f1) + "\n")

output_file.write("Accuracy :\t" + str(acc) + "\n")
output_file.write("Precision :\t" + str(prec) + "\n")
output_file.write("Recall :\t" + str(rec) + "\n")
output_file.write("F1 Measure :\t" + str(f1) + "\n")

output_file.close()
