
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
	print "No statistics to show."
	print "All the numbers are zero."
	exit()

#------------------------------------------------------------------

output_file = open(output_file_name, 'w')

print "\n"
print "True Positive:", tp
print "True Negative:", tn
print "False Positive:", fp
print "False Negative:", fn

output_file.write("True Positive: " + str(tp) + "\n")
output_file.write("True Negative: " + str(tn) + "\n")
output_file.write("False Positive: " + str(fp) + "\n")
output_file.write("False Negative: " + str(fn) + "\n")

print "\n----------------------------------\n"
output_file.write("\n----------------------------------\n")

print "Accuracy :\t\t", (tp + tn)/(tp + tn + fp + fn)
print "Balanced Acc :\t", 0.5 * (tp/(tp + fn) + tn/(tn + fp))
print "Precision :\t\t", tp/(tp + fp)
print "Recall :\t\t", tp/(tp + fn)
print "F1 Measure :\t\t", (2. * tp)/((2. * tp) + fp + fn)

output_file.write("Accuracy :\t\t" + str((tp + tn)/(tp + tn + fp + fn)) + "\n")
output_file.write("Balanced Acc :\t" + str(0.5 * (tp/(tp + fn) + tn/(tn + fp))) + "\n")
output_file.write("Precision :\t\t" + str(tp/(tp + fp)) + "\n")
output_file.write("Recall :\t\t" + str(tp/(tp + fn)) + "\n")
output_file.write("F1 Measure :\t" + str((2. * tp)/((2. * tp) + fp + fn)) + "\n")

print "\nWith neutrals as accepted:"
print "--------------------------\n"
output_file.write("\nWith neutrals as accepted:\n")
output_file.write("--------------------------\n\n")

print "Accuracy :\t\t", (tp + n_acc_tp + tn)/(tp + n_acc_tp + tn + fp + n_acc_fp + fn)
print "Precision :\t\t", (tp + n_acc_tp)/(tp + n_acc_tp + fp + n_acc_fp)
print "Recall :\t\t", (tp + n_acc_tp)/(tp + n_acc_tp + fn)
print "F1 Measure :\t\t", (2. * (tp + n_acc_tp))/(2. * (tp + n_acc_tp) + fp + n_acc_fp + fn)

output_file.write("Accuracy :\t\t" + str((tp + n_acc_tp + tn)/(tp + n_acc_tp + tn + fp + n_acc_fp + fn)) + "\n")
output_file.write("Precision :\t\t" + str((tp + n_acc_tp)/(tp + n_acc_tp + fp + n_acc_fp)) + "\n")
output_file.write("Recall :\t\t" + str((tp + n_acc_tp)/(tp + n_acc_tp + fn)) + "\n")
output_file.write("F1 Measure :\t" + str((2. * (tp + n_acc_tp))/(2. * (tp + n_acc_tp) + fp + n_acc_fp + fn)) + "\n")

print "\nWith neutrals as rejected:"
print "--------------------------\n"
output_file.write("\nWith neutrals as rejected:\n")
output_file.write("--------------------------\n\n")

print "Accuracy :\t\t", (tp + tn + n_rej_tn)/(tp + tn + n_rej_tn + fp + fn + n_rej_fn)
print "Precision :\t\t", tp/(tp + fp)
print "Recall :\t\t", tp/(tp + fn + n_rej_fn)
print "F1 Measure :\t", (2. * tp)/((2. * tp) + fp + fn + n_rej_fn)

output_file.write("Accuracy :\t\t" + str((tp + tn + n_rej_tn)/(tp + tn + n_rej_tn + fp + fn + n_rej_fn)) + "\n")
output_file.write("Precision :\t\t" + str(tp/(tp + fp)) + "\n")
output_file.write("Recall :\t\t" + str(tp/(tp + fn + n_rej_fn)) + "\n")
output_file.write("F1 Measure :\t\t" + str((2. * tp)/((2. * tp) + fp + fn + n_rej_fn)) + "\n")

output_file.close()
