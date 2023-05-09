# Table 2. Performance of data-driven Infer.

## Instructions
1. Collect training data. This process needs a long time to collect data. When the given time budget expires, you must manually kill this process.
```bash
./prepare.sh
```

2. Train the model from the collected data.
```bash
./finalize.sh
```

3. Analyze the program with the trained model
```bash
./run.sh
```

4. Create the result table:
```bash
./make_report.sh
```
