for f in *.py
do
    echo "Testing module: "${f}
    python ${f} --test
done
