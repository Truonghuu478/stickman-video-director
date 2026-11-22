import React from 'react';
import {
  AbsoluteFill, Composition, OffthreadVideo, Series, registerRoot, staticFile,
} from 'remotion';

function Episode({shots}) {
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Series>
        {shots.map(({src, trimBefore, durationInFrames}, index) => (
          <Series.Sequence key={index} durationInFrames={durationInFrames}>
            <OffthreadVideo src={staticFile(src)} trimBefore={trimBefore}
              style={{width: '100%', height: '100%', objectFit: 'contain'}} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
}

function Root() {
  return <Composition id="Episode" component={Episode} fps={24} width={720} height={1280}
    defaultProps={{shots: []}}
    calculateMetadata={({props}) => ({
      durationInFrames: props.shots.reduce((sum, shot) => sum + shot.durationInFrames, 0),
    })} />;
}

registerRoot(Root);
