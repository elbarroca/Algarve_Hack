"use client";

import React, { useState } from 'react';
import { SeekerProfile } from '../types/api';

interface RoommateProfileFormProps {
  onProfileComplete: (profile: SeekerProfile) => void;
  initialProfile?: Partial<SeekerProfile>;
}

export const RoommateProfileForm: React.FC<RoommateProfileFormProps> = ({
  onProfileComplete,
  initialProfile,
}) => {
  const [profile, setProfile] = useState<Partial<SeekerProfile>>({
    budget_max: initialProfile?.budget_max || 800,
    schedule: initialProfile?.schedule || 'standard',
    pets: initialProfile?.pets || false,
    smoking: initialProfile?.smoking || false,
    wfh_days: initialProfile?.wfh_days || 0,
    cleanliness: initialProfile?.cleanliness || 'med',
    noise_tolerance: initialProfile?.noise_tolerance || 'med',
    preferred_cities: initialProfile?.preferred_cities || ['Faro', 'Loulé'],
  });

  const [step, setStep] = useState(1);
  const totalSteps = 3;

  const algarveCities = ['Faro', 'Loulé', 'Portimão', 'Lagos', 'Albufeira', 'Tavira', 'Silves', 'Vila do Bispo', 'Vila Real de Santo António', 'Alcoutim', 'Aljezur', 'Castro Marim', 'Lagoa', 'Monchique', 'Olhão', 'São Brás de Alportel'];

  const handleCityToggle = (city: string) => {
    const currentCities = profile.preferred_cities || [];
    if (currentCities.includes(city)) {
      setProfile({
        ...profile,
        preferred_cities: currentCities.filter((c) => c !== city),
      });
    } else {
      setProfile({
        ...profile,
        preferred_cities: [...currentCities, city],
      });
    }
  };

  const handleSubmit = () => {
    if (profile.budget_max && profile.schedule && profile.preferred_cities) {
      onProfileComplete(profile as SeekerProfile);
    }
  };

  const canProceed = () => {
    if (step === 1) {
      return profile.budget_max && (profile.preferred_cities?.length || 0) > 0;
    }
    return true;
  };

  return (
    <div className="bg-slate-800/40 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">
          Perfil de Compatibilidade 🤝
        </h2>
        <p className="text-slate-300 text-sm">
          Ajude-nos a encontrar a casa e colegas ideais para si
        </p>
        <div className="flex gap-2 justify-center mt-4">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`h-2 w-12 rounded-full ${
                i + 1 <= step ? 'bg-blue-500' : 'bg-slate-600'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Step 1: Budget & Location */}
      {step === 1 && (
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-3">
              💰 Orçamento máximo mensal
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="300"
                max="2000"
                step="50"
                value={profile.budget_max || 800}
                onChange={(e) =>
                  setProfile({ ...profile, budget_max: parseInt(e.target.value) })
                }
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
              />
              <span className="text-2xl font-bold text-blue-400 min-w-[100px]">
                {profile.budget_max}€
              </span>
            </div>
          </div>

          <div>
            <label className="block text-white font-medium mb-3">
              📍 Cidades preferidas (selecione 1 ou mais)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {algarveCities.map((city) => (
                <button
                  key={city}
                  onClick={() => handleCityToggle(city)}
                  className={`px-4 py-2 rounded-lg border-2 transition-all ${
                    profile.preferred_cities?.includes(city)
                      ? 'border-blue-500 bg-blue-500/20 text-blue-300'
                      : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  {city}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 2: Lifestyle */}
      {step === 2 && (
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-3">
              ⏰ Horário de sono
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'early', label: 'Cedo', desc: '22:00-06:00' },
                { value: 'standard', label: 'Normal', desc: '23:00-07:00' },
                { value: 'late', label: 'Tarde', desc: '01:00-09:00' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setProfile({ ...profile, schedule: option.value as any })}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    profile.schedule === option.value
                      ? 'border-blue-500 bg-blue-500/20 text-white'
                      : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold">{option.label}</div>
                  <div className="text-xs text-slate-400">{option.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-white font-medium mb-3">
              💼 Dias de teletrabalho por semana
            </label>
            <div className="flex gap-2">
              {[0, 1, 2, 3, 4, 5].map((days) => (
                <button
                  key={days}
                  onClick={() => setProfile({ ...profile, wfh_days: days })}
                  className={`flex-1 px-4 py-2 rounded-lg border-2 transition-all ${
                    profile.wfh_days === days
                      ? 'border-blue-500 bg-blue-500/20 text-white'
                      : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  {days === 0 ? 'Nenhum' : days}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                profile.pets
                  ? 'border-blue-500 bg-blue-500/20'
                  : 'border-slate-600 bg-slate-700/30 hover:border-slate-500'
              }">
                <input
                  type="checkbox"
                  checked={profile.pets || false}
                  onChange={(e) => setProfile({ ...profile, pets: e.target.checked })}
                  className="w-5 h-5 accent-blue-500"
                />
                <div>
                  <div className="text-white font-medium">🐕 Tenho animais</div>
                  <div className="text-xs text-slate-400">de estimação</div>
                </div>
              </label>
            </div>

            <div>
              <label className="flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all ${
                profile.smoking
                  ? 'border-blue-500 bg-blue-500/20'
                  : 'border-slate-600 bg-slate-700/30 hover:border-slate-500'
              }">
                <input
                  type="checkbox"
                  checked={profile.smoking || false}
                  onChange={(e) => setProfile({ ...profile, smoking: e.target.checked })}
                  className="w-5 h-5 accent-blue-500"
                />
                <div>
                  <div className="text-white font-medium">🚬 Fumador</div>
                  <div className="text-xs text-slate-400">fumo regularmente</div>
                </div>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Preferences */}
      {step === 3 && (
        <div className="space-y-6">
          <div>
            <label className="block text-white font-medium mb-3">
              🧹 Preferência de limpeza
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'low', label: 'Relaxado', emoji: '😌' },
                { value: 'med', label: 'Moderado', emoji: '🙂' },
                { value: 'high', label: 'Muito limpo', emoji: '✨' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setProfile({ ...profile, cleanliness: option.value as any })}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    profile.cleanliness === option.value
                      ? 'border-blue-500 bg-blue-500/20 text-white'
                      : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="text-2xl mb-1">{option.emoji}</div>
                  <div className="text-sm font-semibold">{option.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-white font-medium mb-3">
              🔊 Tolerância ao ruído
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'low', label: 'Silêncio', emoji: '🤫' },
                { value: 'med', label: 'Moderado', emoji: '🙂' },
                { value: 'high', label: 'Tolerante', emoji: '🎉' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() =>
                    setProfile({ ...profile, noise_tolerance: option.value as any })
                  }
                  className={`p-3 rounded-lg border-2 transition-all ${
                    profile.noise_tolerance === option.value
                      ? 'border-blue-500 bg-blue-500/20 text-white'
                      : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                  }`}
                >
                  <div className="text-2xl mb-1">{option.emoji}</div>
                  <div className="text-sm font-semibold">{option.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-200">
            💡 <strong>Nota:</strong> Usamos estas informações apenas para calcular compatibilidade.
            Os seus dados são privados e seguem o RGPD.
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="flex gap-3 pt-4">
        {step > 1 && (
          <button
            onClick={() => setStep(step - 1)}
            className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-lg transition-all"
          >
            ← Voltar
          </button>
        )}
        {step < totalSteps ? (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Continuar →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-semibold rounded-lg transition-all"
          >
            ✓ Concluir Perfil
          </button>
        )}
      </div>
    </div>
  );
};


