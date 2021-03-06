import argparse
import sys
import os
import json
from time import strftime


evidence_guide = {
    "EXP": "Inferred from Experiment (EXP)",
    "IDA": "Inferred from Direct Assay (IDA)",
    "IPI": "Inferred from Physical Interaction (IPI)",
    "IMP": "Inferred from Mutant Phenotype (IMP)",
    "IGI": "Inferred from Genetic Interaction (IGI)",
    "IEP": "Inferred from Expression Pattern (IEP)",
    "HTP": "Inferred from High Throughput Experiment (HTP)",
    "HDA": "Inferred from High Throughput Direct Assay (HDA)",
    "HMP": "Inferred from High Throughput Mutant Phenotype (HMP)",
    "HGI": "Inferred from High Throughput Genetic Interaction (HGI)",
    "HEP": "Inferred from High Throughput Expression Pattern (HEP)",
    "IBA": "Inferred from Biological aspect of Ancestor (IBA)",
    "IBD": "Inferred from Biological aspect of Descendant (IBD)",
    "IKR": "Inferred from Key Residues (IKR)",
    "IRD": "Inferred from Rapid Divergence (IRD)",
    "ISS": "Inferred from Sequence or structural Similarity (ISS)",
    "ISO": "Inferred from Sequence Orthology (ISO)",
    "ISA": "Inferred from Sequence Alignment (ISA)",
    "ISM": "Inferred from Sequence Model (ISM)",
    "IGC": "Inferred from Genomic Context (IGC)",
    "RCA": "Inferred from Reviewed Computational Analysis (RCA)",
    "TAS": "Traceable Author Statement (TAS)",
    "NAS": "Non-traceable Author Statement (NAS)",
    "IC": "Inferred by Curator (IC)",
    "ND": "No biological Data available (ND)",
    "IEA": "Inferred from Electronic Annotation (IEA)"
}

source_dbs = {
    "UniProtKB": "uniprotac",
    "FB": "flybase",
    "MGI": "mouse genome informatics",
    "RGD": "rat genome database",
    "SGD": "saccharomyces genome database",
    "WB": "wormbase database of nematode biology"
}


def parse_args(args):
    help_text = \
        """
        === GO Annotations Loader script ===
        
        **Description:**

        This script takes a GAF GO Annotation file, which contains annotations
        and converts it to Sherlock compatible JSON format.
        
        We keep only the following information from the GAF file:
        - column1: DB
        - column2: DB Object ID
        - column5: GO ID
        - column7: Evidence Code
                
        
        **Parameters:**
        
        -i, --input-file <path>         : path to an existing .gaf file [mandatory]
        
        -t, --tax-id <int>              : taxonomy identifier [mandatory]
        
        
        **Exit codes**
        
        Exit code 1: The specified input file does not exists!
        Exit code 2: The specified input file is not a GAF file!
        """

    parser = argparse.ArgumentParser(description=help_text)

    parser.add_argument("-i", "--input-file",
                        help="<path to an existing .gaf file> [mandatory]",
                        type=str,
                        dest="input_file",
                        action="store",
                        required=True)

    parser.add_argument("-t", "--tax-id",
                        help="<taxonomy identifier> [mandatory]",
                        type=int,
                        dest="tax_id",
                        action="store",
                        required=True)

    results = parser.parse_args(args)

    return results.input_file, results.tax_id


def check_params(input_file):

    if not os.path.isfile(input_file):
        sys.stderr.write(f"ERROR MESSAGE: The specified input file does not exists: {input_file}")
        sys.exit(1)

    if not input_file.endswith(".gaf"):
        sys.stderr.write(f"ERROR MESSAGE: The specified input file is not a GAF file: {input_file}")
        sys.exit(2)


def write_to_output(line, out):

    json_dictionary = {}

    if "MGI" in line[1]:
        json_dictionary["id"] = line[1].split(":")[1]
    else:
        json_dictionary["id"] = line[1]

    json_dictionary["id_type"] = source_dbs[line[0]]
    json_dictionary["go_id"] = int(line[4].split(":")[1])
    json_dictionary["evidence"] = evidence_guide[line[6]]

    out.write(json.dumps(json_dictionary) + '\n')


def main():

    input_file, tax_id = parse_args(sys.argv[1:])

    check_params(input_file)
    print(f'MESSSAGE [{strftime("%H:%M:%S")}]: Parameters are fine, starting...')

    output_folder = input_file.split("/")[:-1]
    output_folder = "".join(output_folder)
    new_folder = os.path.join(output_folder, f'tax_id={tax_id}')
    if not os.path.isdir(new_folder):
        os.mkdir(new_folder)

    output_file = os.path.join(new_folder, f'go_annotations.json')
    abspath_output_file = os.path.abspath(output_file)

    with open(input_file, 'r') as f, open(output_file, 'w') as out:

        num_lines = sum(1 for line in open(input_file))
        checking_array = {}
        iteration = 0

        print(f'MESSSAGE [{strftime("%H:%M:%S")}]: Writing interactions to output file: {abspath_output_file}')
        for line in f:

            percent = int((iteration / num_lines) * 100)
            sys.stdout.write(f'\rMESSAGE: {iteration} / {num_lines} lines are processed | {percent}% done!')
            iteration += 1

            if line.startswith("!"):
                continue

            else:
                line = line.strip().split('\t')
                checking_columns = ",".join([line[0], line[1], line[4], line[6]])
                if checking_columns in checking_array:
                    continue
                checking_array[checking_columns] = True
                write_to_output(line, out)

    sys.stdout.write(f'\rMESSAGE {num_lines} / {num_lines} lines are processed| 100% done!')
    print(f'\nMESSSAGE [{strftime("%H:%M:%S")}]: GO Annotations Loader script finished successfully!')


if __name__ == '__main__':
    main()
