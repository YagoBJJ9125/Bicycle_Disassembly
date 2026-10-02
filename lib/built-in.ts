import { bundleSchema, type Bundle } from './catalog';
import { demoBundle } from './demo';
import cityExample from '@/data/elops-study-v1.json';

const example = bundleSchema.parse(cityExample);
export const builtInBundle:Bundle={
  schemaVersion:1,
  structures:[...example.structures,...demoBundle.structures],
  bikes:[...example.bikes,...demoBundle.bikes],
};
