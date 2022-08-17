const fs = require('fs');
const path = require('path');
const _ = require('lodash');

module.exports = {
  'generate:after': generator => {
    const asyncapi = generator.asyncapi;
    let hasSchema = false;

    const package = `${_.snakeCase(asyncapi.info().title())}_client`;
    const packagePath = path.resolve(generator.targetDir, package);
    fs.rmSync(packagePath, { recursive: true, force: true });
    fs.renameSync(path.resolve(generator.targetDir, 'package'), packagePath);

    if (asyncapi.components()) {
      for (const schema in asyncapi.components().schemas()) {
        hasSchema = true;
        let oldName = schema + '.py';
        let newName = _.lowerFirst(oldName);
        if (newName !== schema) {
          fs.renameSync(path.resolve(packagePath, oldName), path.resolve(packagePath, newName));
        }
      }
    }

    // If there are no schemas, we expect to find an anonymous one embedded in a payload. If we do have schemas we assume we don't need this.
    // This will turn out to be a bug if we ever have a file with schemas, but which also has an anonymous schema embedded in an operation.
    if (hasSchema) {
      fs.unlinkSync(path.resolve(packagePath, 'payload.py'));
    }
  }
}
