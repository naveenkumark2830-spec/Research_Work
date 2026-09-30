import React from 'react';
import { AstraOrb, AstraOrbMode } from './AstraOrb';

export type TeddyOrbMode = AstraOrbMode;

interface TeddyOrbProps {
  mode: TeddyOrbMode;
  amplitude?: number;
  onClick?: () => void;
}

export const TeddyOrb: React.FC<TeddyOrbProps> = ({ mode, amplitude, onClick }) => {
  return <AstraOrb mode={mode} amplitude={amplitude} onClick={onClick} />;
};
