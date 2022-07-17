PROTO_SCHEMA=graph.proto
PROTO_BUNDLE=bundle.json
PROTO_DIR=proto
BUNDLE_DIR=app/public

# Delete previously generated code
echo "Deleting previously generated code."
if [ -d "$PROTO_CLASSES_DIR" ]; then rm -r $PROTO_CLASSES_DIR; fi

# Compile into generated code & stubs
# echo "Compiling proto schema."
# echo "protoc --python_out=$PROTO_DIR --mypy_out=$PROTO_CLASSES_DIR $PROTO_SCHEMA"
echo "Compiling new proto classes & stubs."
mkdir $PROTO_CLASSES_DIR
protoc -I=$PROTO_DIR --python_out=$PROTO_DIR/classes --mypy_out=$PROTO_DIR/classes $PROTO_DIR/$PROTO_SCHEMA

# Update the front-end bundle as well
echo "Updating front-end bundle."
pbjs -t json $PROTO_DIR/$PROTO_SCHEMA > $BUNDLE_DIR/$PROTO_BUNDLE

echo "Done."
