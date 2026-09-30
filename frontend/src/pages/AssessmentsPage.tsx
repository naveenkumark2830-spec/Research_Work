import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';

export const AssessmentsPage: React.FC = () => {
  const [selectedOption, setSelectedOption] = useState<number | null>(1);
  const [submitted, setSubmitted] = useState(false);

  const question = {
    number: '04 / 10',
    topic: 'HDFS Fundamentals',
    text: 'Which component in the HDFS cluster architecture manages filesystem metadata and block locations?',
    options: [
      'DataNode',
      'NameNode',
      'NodeManager',
      'Reducer'
    ],
    correctIndex: 1,
    teddyExplanation: 'Exactly. The NameNode maintains the filesystem namespace, directory tree, file-to-block mapping, and block locations across DataNodes.'
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div>
        <div style={{ fontSize: '22px', fontWeight: 800, color: '#ffffff', marginBottom: '6px' }}>
          Assessments & Quizzes
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8' }}>
          Test your mastery of HDFS block storage, fault tolerance, MapReduce execution, and YARN scheduling.
        </div>
      </div>

      {/* Quiz Question Card */}
      <div style={{
        backgroundColor: '#0e1526',
        border: '1px solid #1e2942',
        borderRadius: '12px',
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px'
      }}>
        {/* Progress & Topic Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{
            fontSize: '11px',
            fontWeight: 700,
            color: '#00f0ff',
            backgroundColor: 'rgba(0, 240, 255, 0.1)',
            padding: '3px 10px',
            borderRadius: '4px',
            fontFamily: "'JetBrains Mono', monospace"
          }}>
            {question.topic}
          </span>
          <span style={{ fontSize: '12px', color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace", fontWeight: 700 }}>
            Question {question.number}
          </span>
        </div>

        {/* Question Text */}
        <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#ffffff', lineHeight: '1.4' }}>
          {question.text}
        </h3>

        {/* Options List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {question.options.map((opt, idx) => {
            const isSelected = selectedOption === idx;
            const isCorrect = idx === question.correctIndex;
            let bgColor = '#131c31';
            let borderColor = '#1e2942';

            if (submitted) {
              if (isCorrect) {
                bgColor = 'rgba(34, 197, 94, 0.15)';
                borderColor = '#22c55e';
              } else if (isSelected) {
                bgColor = 'rgba(239, 68, 68, 0.15)';
                borderColor = '#ef4444';
              }
            } else if (isSelected) {
              bgColor = 'rgba(0, 240, 255, 0.1)';
              borderColor = '#00f0ff';
            }

            return (
              <button
                key={idx}
                onClick={() => !submitted && setSelectedOption(idx)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '14px 16px',
                  borderRadius: '8px',
                  backgroundColor: bgColor,
                  border: `1px solid ${borderColor}`,
                  color: isSelected || (submitted && isCorrect) ? '#ffffff' : '#cbd5e1',
                  fontSize: '14px',
                  cursor: submitted ? 'default' : 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
              >
                <div style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  border: `2px solid ${isSelected ? '#00f0ff' : '#475569'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: isSelected ? '#00f0ff' : 'transparent',
                  flexShrink: 0
                }}>
                  {isSelected && <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#070a12' }} />}
                </div>
                <span>{opt}</span>
              </button>
            );
          })}
        </div>

        {/* Action Button */}
        {!submitted ? (
          <button
            onClick={() => setSubmitted(true)}
            disabled={selectedOption === null}
            style={{
              marginTop: '12px',
              padding: '12px 24px',
              backgroundColor: '#00f0ff',
              color: '#070a12',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 700,
              cursor: selectedOption === null ? 'not-allowed' : 'pointer',
              opacity: selectedOption === null ? 0.5 : 1,
              boxShadow: '0 0 15px rgba(0, 240, 255, 0.3)'
            }}
          >
            Submit Answer
          </button>
        ) : (
          /* TEDDY Feedback Quote */
          <div style={{
            marginTop: '12px',
            backgroundColor: '#131c31',
            border: '1px solid rgba(0, 240, 255, 0.3)',
            borderRadius: '8px',
            padding: '16px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}>
            <Sparkles size={20} color="#00f0ff" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#00f0ff', marginBottom: '4px' }}>
                TEDDY Assessment Feedback
              </div>
              <div style={{ fontSize: '13px', color: '#f8fafc', lineHeight: '1.5' }}>
                "{question.teddyExplanation}"
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
